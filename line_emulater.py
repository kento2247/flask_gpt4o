import argparse
import json

from src.message_flow import message_flow


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
    parser.add_argument(
        "--user_id",
        type=str,
        default="U4db8598c517126f763da9e261203650a",
        help="Line user id",
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


def make_json(
    user_message: str, line_id: str = "U4db8598c517126f763da9e261203650a"
) -> dict:
    return {
        "events": [
            {
                "type": "message",
                "replyToken": "local",
                "source": {
                    "userId": line_id,
                    "type": "user",
                },
                "timestamp": 1634668400000,
                "mode": "active",
                "message": {
                    "type": "text",
                    "id": "14008782937777",
                    "text": user_message,
                },
            }
        ]
    }


def main(args):
    message_flow_client.message_parser(make_json("resume", args.user_id))
    while True:
        user_message = input("User: ")
        request_json = make_json(user_message, args.user_id)

        result = message_flow_client.message_parser(
            request_json
        )  # result==Falseの場合はインタビュー終了
        if result is False:
            break


if __name__ == "__main__":
    args = parser()

    # mongodb, line, gptの初期化
    message_flow_client = message_flow(args)

    main(args)
