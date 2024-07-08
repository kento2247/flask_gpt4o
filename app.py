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
messages = []


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/callback", methods=["POST"])
def callback():
    # リクエストボディを取得
    body = request.json
    events = body.get("events", [])
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            if len(messages) == 0:
                messages.append(
                    {
                        "role": "system",
                        "content": "あなたは職場を取材するインタビュアーです．行動の背景要因や思いの深層を嫌がられずに聞き出すことが目的です．チャットを開始してください．長文を送らないように気をつけること．",
                    }
                )
            else:
                user_message = event["message"]["text"]
                messages.append({"role": "user", "content": user_message})

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    response = response.choices[0].message.content
    reply_message(reply_token, response)
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
    app.run(host="0.0.0.0", port=3000)
