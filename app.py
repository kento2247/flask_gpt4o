import argparse
import json

from flask import Flask, render_template, request

from src.message_flow import message_flow

app = Flask(__name__)
args = None
message_flow_client = None


@app.route("/callback", methods=["POST"])
def callback():
    print("callback")
    message_flow_client.message_parser(request.json)
    return "OK"


@app.route("/keep_alive", methods=["GET"])
def keep_alive():
    print("keep_alive")
    return "OK"


@app.route("/friend_list", methods=["get"])
def friend_list():
    print("friend_list")
    line_ids = message_flow_client.mongo_db_client.sessionid_dict.keys()
    friend_list = []
    for line_id in line_ids:
        profile = message_flow_client.line_client.get_profile(line_id)
        friend_list.append(profile)
    return render_template("friend_list.html", friend_list=friend_list)


@app.route("/interview_history", methods=["get"])
def interview_history():
    print("interview_history")
    line_id = request.args.get("userId")
    displayName = request.args.get("displayName")
    interview_history = message_flow_client.mongo_db_client.get_messages(line_id)
    return render_template(
        "interview_history.html",
        interview_history=interview_history,
        displayName=displayName,
    )


@app.route("/delete_sessionid", methods=["post"])
def delete_sessionid():
    print("delete_sessionid")
    session_id = request.json.get("session_id")
    message_flow_client.mongo_db_client.delete_sessionid(session_id)
    return "OK"


@app.route("/interview_history_json", methods=["get"])
def interview_history_json():
    print("interview_history_json")
    session_id = request.args.get("session_id")
    interview_history = message_flow_client.mongo_db_client.get_one_messages_session_id(
        session_id
    )
    response = app.response_class(
        response=json.dumps(
            {"interview_history": interview_history}, ensure_ascii=False, indent=4
        ),
        mimetype="application/json",
    )
    response.headers["Content-Disposition"] = (
        f"attachment; filename=messages_{session_id}.json"
    )
    return response


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
