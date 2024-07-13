import argparse
import os

import requests
import yaml
from dotenv import load_dotenv

from src.line import line
from src.mongodb import mongodb

config = None
mongo_db_client = None


def server_test():
    endpoint = "http://192.168.0.12:3011/callback"
    data = {
        "destination": "xxxxxxxxxx",
        "events": [
            {
                "replyToken": "85cbe770fa8b4f45bbe077b1d4be4a36",
                "type": "follow",
                "mode": "active",
                "timestamp": 1705891467176,
                "source": {
                    "type": "user",
                    "userId": "Uaedb10ed004057a7f73606b62ecfc6f7",
                },
                "webhookEventId": "01HMQGW40RZJPJM3RAJP7BHC2Q",
                "deliveryContext": {"isRedelivery": False},
                "follow": {"isUnblocked": False},
            }
        ],
    }

    response = requests.post(endpoint, json=data)
    print(response.text)


def del_mongodb_lineid(line_id: str):
    mongo_db_client.delete_lineid(line_id)


def line_push_demo(line_id: str):
    line_client.push_gpt_response(line_id, "test", "test")


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

    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_client = line(channel_access_token)

    del_mongodb_lineid("Uaedb10ed004057a7f73606b62ecfc6f7")
    # line_push_demo("Uaedb10ed004057a7f73606b62ecfc6f7")
