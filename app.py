import argparse
import os

import yaml
from dotenv import load_dotenv
from flask import Flask, request

from src.gpt import gpt
from src.line import line
from src.mongodb import mongodb

app = Flask(__name__)
args = None
mongo_db_client = None
line_client = None
gpt_client = None


def line_gpt_response(messages: list, line_id: str, reply_token: str, session_id: str):
    try:
        response_text = gpt_client.get_response(messages)
        line_client.reply_gpt_response(
            reply_token=reply_token, session_id=session_id, message=response_text
        )  # lineでの返信
        content_dict = {"role": "assistant", "content": response_text}
        mongo_db_client.insert_message(line_id, content_dict)  # 会話履歴の更新
    except Exception as e:
        response_text += f"エラーが発生しました．\n{e}"
        app.logger.error(e)
        line_client.reply(reply_token, response_text)


@app.route("/callback", methods=["POST"])
def callback():
    line_id = ""
    reply_token = ""
    session_id = ""
    messages = []

    # リクエストボディを取得
    body = request.json
    events = body.get("events", [])

    for event in events:
        print(event)
        reply_token = event["replyToken"]
        line_id = event["source"]["userId"]
        session_id = mongo_db_client.sessionid_dict[line_id]

        if event["type"] == "message" and event["message"]["type"] == "text":
            messages = mongo_db_client.get_messages(line_id)  # 会話履歴の取得
            if len(messages) == 1:  # 初回メッセージ，またはリセット後のメッセージ
                line_gpt_response(messages, line_id, reply_token, session_id)
                break
            else:  # 2回目以降のメッセージ
                user_message = event["message"]["text"]
                if user_message == "exit":  # 会話履歴のリセット
                    line_client.reply_interview_end(reply_token)
                    mongo_db_client.initialize_messages(line_id)
                    break
                else:  # 通常の会話
                    content_dict = {"role": "user", "content": user_message}
                    messages.append(content_dict)
                    line_gpt_response(messages, line_id, reply_token, session_id)
                    mongo_db_client.insert_message(line_id, content_dict)
                    break

        # 友達追加やブロック解除のイベント
        elif event["type"] == "follow":
            messages = [
                {
                    "role": "system",
                    "content": config["initial_message"],
                }
            ]
            line_gpt_response(messages, line_id, reply_token, session_id)
            mongo_db_client.initialize_messages(line_id)
            break

    return "OK"


@app.route("/keep_alive", methods=["GET"])
def keep_alive():
    return "OK"


if __name__ == "__main__":
    config = yaml.safe_load(open("config.yaml"))

    # コマンドライン引数の取得
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load_env",
        action="store_true",
        help="Load environment variables from .env file",
    )
    parser.add_argument(
        "--sleep_api",
        action="store_true",
        help="Sleep OpenAI API",
    )
    args = parser.parse_args()

    # 環境変数の読み込み
    if args.load_env:
        load_dotenv()

    # mongodb接続設定
    mongodb_username = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_app_name = config["mongodb"]["app_name"]
    mongodb_db_name = config["mongodb"]["db_name"]
    mongo_db_client = mongodb(
        username=mongodb_username,
        password=mongodb_password,
        app_name=mongodb_app_name,
        db_name=mongodb_db_name,
    )

    # line接続設定
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_client = line(channel_access_token)

    print(line_client.reply_gpt_response("test", "test", "test"))

    # gpt接続設定
    gpt_model = config["gpt"]["model"]
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gpt_client = gpt(model=gpt_model, api_key=openai_api_key)

    # サーバーの起動
    server_port = config["server"]["port"]
    app.run(host="0.0.0.0", port=server_port)
