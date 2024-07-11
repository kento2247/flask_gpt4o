import argparse
import os
import uuid

import openai
import requests
from dotenv import load_dotenv
from flask import Flask, request
from pymongo.mongo_client import MongoClient

app = Flask(__name__)

INITIAL_MESSAGE = [
    {
        "role": "system",
        "content": "あなたは職場を取材するインタビュアーです．行動の背景要因や思いの深層を嫌がられずに聞き出すことが目的です．チャットを開始してください．長文を送らないように気をつけること．",
    }
]


def get_gpt_response(messages: list) -> str:
    if args.sleep_api:
        response_str = "現在休止中"
    else:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        response_str = response.choices[0].message.content
    return response_str


class mongo_db:
    def __init__(self):
        self.MONGO_USERNAME = os.getenv("MONGO_USERNAME")
        self.MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
        self.MONGO_URI = f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@gpt4otest.aartxch.mongodb.net/?retryWrites=true&w=majority&appName=gpt4otest"
        self.client = MongoClient(self.MONGO_URI)
        self.db = self.client["gpt4otest"]["messages"]
        self.sessionid_dict = {}

        # endが存在しないcollectionの一覧を取得
        session_count = self.db.count_documents({"end": {"$exists": False}})
        if session_count > 0:
            sessions = self.db.find({"end": {"$exists": False}})
            for session in sessions:
                line_id = session["line_id"]
                session_id = session["session_id"]
                self.sessionid_dict[line_id] = session_id

    def initialize_messages(self, line_id: str) -> None:
        if line_id in self.sessionid_dict:
            session_id = self.sessionid_dict[line_id]
            # 終了記号を追加
            self.db.update_many(
                {"session_id": session_id, "line_id": line_id},
                {"$set": {"end": True}},
            )

        # 新しいセッションを作成
        new_session_id = str(uuid.uuid4())
        new_messages = {
            "session_id": new_session_id,
            "line_id": line_id,
            "data": INITIAL_MESSAGE,
        }
        self.db.insert_one(new_messages)
        self.sessionid_dict[line_id] = new_session_id

    def get_messages(self, line_id: str) -> list:
        if line_id not in self.sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self.sessionid_dict[line_id]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        return messages["data"]

    def insert_message(self, line_id: str, content_dict: dict) -> None:
        if line_id not in self.sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self.sessionid_dict[line_id]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        messages["data"].append(content_dict)
        self.db.update_one(
            {"session_id": session_id, "line_id": line_id},
            {"$set": {"data": messages["data"]}},
        )


mongo_db_client = mongo_db()


@app.route("/callback", methods=["POST"])
def callback():
    # リクエストボディを取得
    body = request.json
    events = body.get("events", [])
    response_text = ""
    messages = []
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            line_id = event["source"]["userId"]
            messages = mongo_db_client.get_messages(line_id)  # 会話履歴の取得
            if len(messages) == 1:
                session_id = mongo_db_client.sessionid_dict[line_id]
                response_text += f"line_id: {line_id}\nsession_id: {session_id}\nexitを送信で会話履歴をリセット\n\n"
            else:
                user_message = event["message"]["text"]
                if user_message == "exit" or user_message == "clear":
                    reply_message(
                        reply_token,
                        "会話履歴をリセットしました．\n何かしらのメッセージの送信で会話を再開．",
                    )
                    mongo_db.initialize_messages(line_id)
                    return "OK"
                else:
                    content_dict = {"role": "user", "content": user_message}
                    mongo_db_client.insert_message(line_id, content_dict)
                    messages.append(content_dict)
        # 友達追加やブロック解除のイベント
        elif event["type"] == "follow":
            reply_token = event["replyToken"]
            line_id = event["source"]["userId"]
            mongo_db_client.initialize_messages(line_id)
            messages = INITIAL_MESSAGE
            session_id = mongo_db_client.sessionid_dict[line_id]
            response_text += f"line_id: {line_id}\nsession_id: {session_id}\nexitを送信で会話履歴をリセット\n\n"
        else:
            return "OK"
    try:
        response_text += get_gpt_response(messages)
        reply_message(reply_token, response_text)  # lineでの返信
        content_dict = {"role": "assistant", "content": response_text}
        mongo_db_client.insert_message(line_id, content_dict)  # 会話履歴の更新
    except Exception as e:
        response_text += f"エラーが発生しました．\n{e}"
        app.logger.error(e)
        reply_message(reply_token, response_text)
    return "OK"


def reply_message(reply_token, user_message):
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
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
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load_env",
        action="store_true",
        help="Load environment variables from .env file",
    )
    args = parser.parse_args()
    if args.load_env:
        load_dotenv()
    # port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=3011)
