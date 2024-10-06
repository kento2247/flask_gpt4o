import json
import os

from line import line


def send_broadcast():
    # このファイルのあるディレクトリの絶対パスを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    relative_broadcast_message_template_path = "../template/broadcast_message.json"
    broadcast_message_template_path = os.path.join(
        current_dir, relative_broadcast_message_template_path
    )
    broadcast_message_template = json.load(open(broadcast_message_template_path))
    line.broadcast_flex_message(broadcast_message_template)


if __name__ == "__main__":
    send_broadcast()
