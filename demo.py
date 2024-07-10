import argparse
import os
import uuid

import openai
import requests
from dotenv import load_dotenv
from flask import Flask, request
from pymongo.mongo_client import MongoClient

load_dotenv()

INITIAL_MESSAGE = [
    {
        "role": "system",
        "content": "あなたは職場を取材するインタビュアーです．行動の背景要因や思いの深層を嫌がられずに聞き出すことが目的です．チャットを開始してください．長文を送らないように気をつけること．",
    }
]


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
            # session_id = self.sessionid_dict[line_id]
            # 終了記号を追加
            self.db.update_many(
                {"line_id": line_id},
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
        self.sessionid_dict["line_id"] = new_session_id

    def get_messages(self, line_id: str) -> list:
        if line_id not in self.sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self.sessionid_dict["line_id"]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        return messages["data"]

    def insert_message(self, line_id: str, content_dict: dict) -> None:
        if line_id not in self.sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self.sessionid_dict["line_id"]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        messages["data"].append(content_dict)
        self.db.update_one(
            {"session_id": session_id, "line_id": line_id},
            {"$set": {"data": messages["data"]}},
        )


mongo_db_client = mongo_db()
print(mongo_db_client.sessionid_dict)
line_id = "Uaedb10ed004057a7f73606b62ecfc6f7"
mongo_db_client.initialize_messages(line_id)
