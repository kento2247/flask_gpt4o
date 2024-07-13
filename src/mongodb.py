import uuid

import yaml
from pymongo.mongo_client import MongoClient


class mongodb:
    def __init__(self, app_name: str, db_name: str, username: str, password: str):
        self.MONGO_USERNAME = username
        self.MONGO_PASSWORD = password
        self.MONGO_URI = f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{app_name}.aartxch.mongodb.net/?retryWrites=true&w=majority&appName={app_name}"
        self.client = MongoClient(self.MONGO_URI)
        self.db = self.client[app_name][db_name]
        self.sessionid_dict = {}
        self.config = yaml.safe_load(open("config.yaml"))

        # endが存在しないcollectionの一覧を取得
        session_count = self.db.count_documents({"end": {"$exists": False}})
        if session_count > 0:
            sessions = self.db.find({"end": {"$exists": False}})
            for session in sessions:
                line_id = session["line_id"]
                session_id = session["session_id"]
                self.sessionid_dict[line_id] = session_id

    def initialize_messages(self, line_id: str) -> None:
        initial_message_json = [
            {
                "role": "system",
                "content": self.config["initial_message"],
            }
        ]
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
            "data": initial_message_json,
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

    def delete_lineid(self, line_id: str) -> None:
        self.db.delete_many({"line_id": line_id})
        return None

    def delete_sessionid(self, line_id: str) -> None:
        session_id = self.sessionid_dict[line_id]
        self.db.delete_many({"session_id": session_id})
        return None
