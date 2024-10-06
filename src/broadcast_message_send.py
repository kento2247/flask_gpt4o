import json
import os

from dotenv import load_dotenv

load_dotenv()
from line import line


def send_broadcast():
    # このファイルのあるディレクトリの絶対パスを取得
    broadcast_message_template_path = "template/broadcast_message.json"
    broadcast_message_template = json.load(open(broadcast_message_template_path))

    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_client = line(channel_access_token)
    line_client.broadcast_flex_message(broadcast_message_template)


if __name__ == "__main__":
    send_broadcast()
