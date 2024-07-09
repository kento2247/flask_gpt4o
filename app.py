import argparse
import os

import openai
import requests
from dotenv import load_dotenv
from flask import Flask, request

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
}
messages_dict = {}


def initialize_messages(id):
    if id not in messages_dict:
        messages_dict[id] = []
    messages_dict[id] = [
        {
            "role": "system",
            "content": "あなたは職場を取材するインタビュアーです．行動の背景要因や思いの深層を嫌がられずに聞き出すことが目的です．チャットを開始してください．長文を送らないように気をつけること．",
        }
    ]


@app.route("/messages")
def messages():
    return messages_dict


@app.route("/callback", methods=["POST"])
def callback():
    # リクエストボディを取得
    body = request.json
    events = body.get("events", [])
    response_text = ""
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            user_id = event["source"]["userId"]
            if user_id not in messages_dict:
                initialize_messages(user_id)
            if len(messages_dict[user_id]) == 1:
                response_text += f"[初めまして{user_id}]\n[exit を送信すると会話履歴をリセットできます]\n"
            else:
                user_message = event["message"]["text"]
                if user_message == "exit" or user_message == "clear":
                    initialize_messages(user_id)
                    reply_message(reply_token, "会話履歴をリセットしました．")
                    return "OK"
                else:
                    messages_dict[user_id].append(
                        {"role": "user", "content": user_message}
                    )
        # 友達追加やブロック解除のイベント
        elif event["type"] == "follow":
            reply_token = event["replyToken"]
            user_id = event["source"]["userId"]
            initialize_messages(user_id)
            response_text += f"[session_id: {user_id}]\n[exit を送信すると会話履歴をリセットできます]\n"
        else:
            return "OK"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages_dict[user_id],
    )
    response_text += response.choices[
        0
    ].message.content  # chatgptの返答テキストのみを抽出
    reply_message(reply_token, response_text)  # lineでの返信
    messages_dict[user_id].append({"role": "assistant", "content": response_text})
    return "OK"


def reply_message(reply_token, user_message):
    reply = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": user_message}],
    }
    response = requests.post(
        "https://api.line.me/v2/bot/message/reply", headers=headers, json=reply
    )
    if response.status_code != 200:
        app.logger.error(f"Error: {response.status_code}, {response.text}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load_env",
        action="store_true",
        help="Load environment variables from .env file",
    )
    args = parser.parse_args()
    if args.load_env:
        load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=3011)
