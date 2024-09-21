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


def line_gpt_response(
    line_id: str, reply_token: str, message: str, progress_max: int = 12
):
    try:
        session_id = mongo_db_client.sessionid_dict[line_id]
        messages = []

        if message == "exit":
            line_client.reply_interview_end(reply_token)
            mongo_db_client.initialize_messages(line_id)
            return
        elif message == "resume":
            messages = mongo_db_client.get_messages(line_id)
            reply_message = ""
            if len(messages) <=1: # exitからの再開の場合
                messages = [
                    {
                        "role": "system",
                        "content": config["initial_message"],
                    }
                ]
                reply_message = gpt_client.get_response(messages)
            else:
                progress = 7
                reply_message = messages[-1]["content"]
            line_client.reply_gpt_response(
                reply_token=reply_token,
                session_id=session_id,
                message=reply_message,
                progress=progress,
                progress_max=progress_max,
            )
            return
        else:
            response_text = ""
            if message == None:
                messages = [
                    {
                        "role": "system",
                        "content": config["initial_message"],
                    }
                ]
                response_text = gpt_client.get_response(messages)
                line_client.reply_gpt_response(
                    reply_token=reply_token,
                    session_id=session_id,
                    message=response_text,
                    progress=0,
                    progress_max=progress_max,
                )  # lineでの返信
                mongo_db_client.initialize_messages(
                    line_id
                )  # 既存のセッションがあれば終了させ，新しいセッションを作成
                return
            else:
                messages = mongo_db_client.get_messages(line_id)  # 会話履歴の取得
                if len(messages) <= 1:  # exitからの再開の場合
                    messages = [
                        {
                            "role": "system",
                            "content": config["initial_message"],
                        }
                    ]
                else:
                    content_dict = {"role": "user", "content": message}
                    messages.append(content_dict)

                response_text = gpt_client.get_response(messages)
                progress = 7
                line_client.reply_gpt_response(
                    reply_token=reply_token,
                    session_id=session_id,
                    message=response_text,
                    progress=progress,
                    progress_max=progress_max,
                )

            content_list = [
                messages[-1],
                {"role": "assistant", "content": response_text},
            ]
            mongo_db_client.insert_message(line_id, content_list)  # 会話履歴の更新

    except Exception as e:
        response_text += f"エラーが発生しました．\n{e}"
        app.logger.error(e)
        line_client.reply(reply_token, response_text)
        # line_client.push_gpt_response(line_id, session_id, "error")


@app.route("/callback", methods=["POST"])
def callback():
    # リクエストボディを取得
    parse_data = line_client.parse_webhook(request.json)

    event_type = parse_data["event_type"]
    line_id = parse_data["line_id"]
    reply_token = parse_data["reply_token"]
    message = parse_data["message"]

    if event_type == "message":
        line_gpt_response(line_id, reply_token, message)
    elif event_type == "follow":
        line_gpt_response(line_id, reply_token, None)

    return "OK"


@app.route("/keep_alive", methods=["GET"])
def keep_alive():
    return "OK"


@app.route("/friend_list", methods=["get"])
def friend_list():
    line_ids = mongo_db_client.sessionid_dict.keys()
    friend_list = []
    for line_id in line_ids:
        profile = line_client.get_profile(line_id)
        friend_list.append(profile)
    print(friend_list)
    return {"friend_list": friend_list}


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

    # gpt接続設定
    gpt_model = config["gpt"]["model"]
    openai_api_key = os.getenv("OPENAI_API_KEY")
    gpt_client = gpt(model=gpt_model, api_key=openai_api_key, sleep_api=args.sleep_api)

    # サーバーの起動
    server_port = config["server"]["port"]
    app.run(host="0.0.0.0", port=server_port)
