import datetime
import json
import os
import uuid

import yaml
from pymongo.mongo_client import MongoClient


class mongodb:
    def __init__(
        self, database_name: str, collection_name: str, username: str, password: str
    ):
        self.database_name = database_name
        self.collection_name = collection_name
        self.MONGO_USERNAME = username
        self.MONGO_PASSWORD = password
        self.MONGO_URI = f"mongodb+srv://{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@{database_name}.aartxch.mongodb.net/?retryWrites=true&w=majority&appName={database_name}"
        self.client = MongoClient(self.MONGO_URI)
        self.db = self.client[database_name][collection_name]
        self._sessionid_dict = {}
        self.config = yaml.safe_load(open("config.yaml"))

        # endが存在しないcollectionの一覧を取得
        session_count = self.db.count_documents({"end": {"$exists": False}})
        if session_count > 0:
            sessions = self.db.find({"end": {"$exists": False}})
            for session in sessions:
                line_id = session["line_id"]
                session_id = session["session_id"]
                self._sessionid_dict[line_id] = session_id

    def initialize_messages(self, line_id: str) -> None:
        if line_id in self._sessionid_dict:
            session_id = self._sessionid_dict[line_id]
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
            "data": [],
            "elements": {},
        }
        self.db.insert_one(new_messages)
        self._sessionid_dict[line_id] = new_session_id

    def get_one_messages_line_id(self, line_id: str) -> list:
        if line_id not in self._sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self._sessionid_dict[line_id]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        return messages

    def get_one_messages_session_id(self, session_id: str) -> list:
        messages = self.db.find_one({"session_id": session_id})
        return messages

    def get_messages(self, line_id: str) -> list:
        # line_idに対応する全てのメッセージを取得
        messages = self.db.find({"line_id": line_id})
        messages = [
            {
                "session_id": message["session_id"],
                "data": message["data"],
                "end": message.get("end", False),
                "elements": message.get("elements", {}),
            }
            for message in messages
        ]
        return messages

    def insert_message(
        self, line_id: str, content_list: list[dict], elements: dict
    ) -> None:
        if type(content_list) is not list:
            content_list = [content_list]
        if line_id not in self._sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self._sessionid_dict[line_id]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        messages["data"].extend(content_list)

        update_data = {
            "data": messages["data"],
        }

        if elements is not None:
            update_data["elements"] = elements

        self.db.update_one(
            {"session_id": session_id, "line_id": line_id},
            {"$set": update_data},
        )

    def update_elements(self, line_id: str, elements: dict) -> None:
        if line_id not in self._sessionid_dict:
            self.initialize_messages(line_id)
        session_id = self._sessionid_dict[line_id]
        messages = self.db.find_one({"session_id": session_id, "line_id": line_id})
        messages["elements"] = elements
        self.db.update_one(
            {"session_id": session_id, "line_id": line_id},
            {"$set": {"elements": messages["elements"]}},
        )

    def delete_lineid(self, line_id: str) -> None:
        self.db.delete_many({"line_id": line_id})
        return None

    def delete_sessionid(self, session_id: str) -> None:
        self.db.delete_many({"session_id": session_id})
        return None

    def all_messages(self) -> list:
        # 全てのメッセージを_id要素を除いて取得
        all_messages_list = []
        for message in self.db.find():
            message.pop("_id")
            all_messages_list.append(message)
        return all_messages_list

    def get_session_id(self, line_id: str) -> str:
        session_id = self._sessionid_dict.get(line_id, None)
        if session_id is None:
            self.initialize_messages(line_id)
            session_id = self._sessionid_dict[line_id]

        return session_id

    def get_line_ids(self) -> list[str]:
        return list(self._sessionid_dict.keys())

    def clear_collection(self, backup_dir_path: str) -> None:
        if backup_dir_path is not None:
            # json形式でバックアップ
            if not os.path.exists(backup_dir_path):
                os.makedirs(backup_dir_path)
            datetime_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"{datetime_now}.json"
            backup_file_path = os.path.join(backup_dir_path, file_name)
            with open(backup_file_path, "w") as f:
                json.dump(self.all_messages(), f, indent=4, ensure_ascii=False)

        # collectionの削除
        self.db.drop()

        # collectionの再作成
        self.db = self.client[self.database_name][self.collection_name]

        return None

    def remove_short_ended_sessions(self) -> int:
        # 全てのメッセージを取得
        all_messages = self.all_messages()

        # 削除対象のsession_idを取得
        session_ids_to_remove = []
        for messages in all_messages:
            if len(messages["data"]) <= 1 and messages.get("end", False):
                session_ids_to_remove.append(messages["session_id"])

        # 対象のline_idのメッセージを削除
        for session_id in session_ids_to_remove:
            self.delete_sessionid(session_id)
            # print(session_id)

        return len(session_ids_to_remove)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    config = yaml.safe_load(open("config.yaml"))
    load_dotenv()

    # mongodb接続設定
    mongodb_username = os.getenv("MONGODB_USERNAME")
    mongodb_password = os.getenv("MONGODB_PASSWORD")
    mongodb_database_name = config["mongodb"]["database_name"]
    mongodb_collection_name = config["mongodb"]["collection_name"]
    mongo_db_client = mongodb(
        username=mongodb_username,
        password=mongodb_password,
        database_name=mongodb_database_name,
        collection_name=mongodb_collection_name,
    )

    # all_messages = mongo_db_client.all_messages()
    # mongo_db_client.clear_collection("backup")

    # dataのlenが<=1で，end=trueのものを消したい

    # 関数の実行
    mongo_db_client.remove_short_ended_sessions()
