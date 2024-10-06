import argparse

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
        print(error_message)
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
    import os

    import yaml
    from dotenv import load_dotenv

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
    parser.add_argument(
        "--config_path",
        type=str,
        default="config.yaml",
        help="Path to config file",
    )
    args = parser.parse_args()

    if args.load_env:
        load_dotenv()

    args.openai_api_key = os.getenv("OPENAI_API_KEY")
    args.mongodb_username = os.getenv("MONGODB_USERNAME")
    args.mongodb_password = os.getenv("MONGODB_PASSWORD")
    args.line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    args.config = yaml.safe_load(open(args.config_path))
    return args


if __name__ == "__main__":
    args = parser()

    # mongodb, line, gptの初期化
    message_flow_client = message_flow(args)

    # サーバーの起動
    server_port = args.config["server"]["port"]
    app.run(host="0.0.0.0", port=server_port)
