import argparse
import os

import yaml
from dotenv import load_dotenv
from flask import Flask, request

from src.message_flow import message_flow

app = Flask(__name__)
args = None
message_flow_client = None


@app.route("/callback", methods=["POST"])
def callback():
    try:
        message_flow_client.message_parser(request.json)
    except Exception as e:
        error_message = f"Error: {e}"
        message_flow_client.error_send(error_message)
    return "OK"


@app.route("/keep_alive", methods=["GET"])
def keep_alive():
    return "OK"


@app.route("/friend_list", methods=["get"])
def friend_list():
    line_ids = message_flow.mongo_db_client.sessionid_dict.keys()
    friend_list = []
    for line_id in line_ids:
        profile = message_flow.line_client.get_profile(line_id)
        friend_list.append(profile)
    print(friend_list)
    return {"friend_list": friend_list}


def parser() -> argparse.Namespace:
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
    return args


if __name__ == "__main__":
    config = yaml.safe_load(open("config.yaml"))
    args = parser()
    args.config = config
    if args.load_env:
        load_dotenv()

    # mongodb, line, gptの初期化
    message_flow_client = message_flow(args)

    # サーバーの起動
    server_port = config["server"]["port"]
    app.run(host="0.0.0.0", port=server_port)
