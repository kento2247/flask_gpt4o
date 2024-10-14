import json
import time

import requests
import yaml


class line:
    def __init__(self, channel_access_token: str):
        self.channnel_access_token = channel_access_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channnel_access_token}",
        }
        self.config = yaml.safe_load(open("config.yaml"))
        self.profile_cache = {}
        self.cache_timestamp = time.time()

    def parse_webhook(self, request_json: dict) -> list:
        response = {
            "event_type": None,
            "line_id": None,
            "reply_token": None,
            "message": None,
        }
        events = request_json.get("events", [])

        for event in events:
            if event["type"] == "message" and event["message"]["type"] == "text":
                response["event_type"] = "message"
                response["line_id"] = event["source"]["userId"]
                response["reply_token"] = event["replyToken"]
                response["message"] = event["message"]["text"]
                break

            # 友達追加やブロック解除のイベント
            elif event["type"] == "follow":
                response["event_type"] = "follow"
                response["line_id"] = event["source"]["userId"]
                response["reply_token"] = event["replyToken"]
                break

        return response

    def reply(self, reply_token: str, message: str):
        if reply_token == "local":
            print("Assistant: ", message)
            return
        response_json = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": message}],
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            raise Exception(response.text)

    def push_message(self, line_id: str, message: str):
        response_json = {
            "to": line_id,
            "messages": [{"type": "text", "text": message}],
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            raise Exception(response.text)

    def get_profile(self, user_id: str) -> dict:
        # キャッシュのクリアを1日おきに行う
        current_time = time.time()
        if current_time - self.cache_timestamp > 86400:  # 86400秒 = 1日
            self.profile_cache.clear()
            self.cache_timestamp = current_time

        # キャッシュを確認して、存在しない場合はAPIから取得
        if user_id in self.profile_cache:
            # print("cache hit: ", user_id)
            return self.profile_cache[user_id]
        else:
            # print("cache miss: ", user_id)
            response = requests.get(
                f"https://api.line.me/v2/bot/profile/{user_id}",
                headers=self.headers,
            )
            if response.status_code == 200:
                profile = response.json()
                self.profile_cache[user_id] = profile
                return profile
            else:
                # raise Exception(response.text)
                sample_profile = {
                    "displayName": "anonymous",
                    "pictureUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/LINE_New_App_Icon_%282020-12%29.png/800px-LINE_New_App_Icon_%282020-12%29.png",
                    "language": "NaN",
                    "userId": user_id,
                    "statusMessage": "ブロック済み",
                }
                return sample_profile

    def reply_gpt_response(
        self,
        reply_token: str,
        session_id: str,
        message: str,
        progress: int = 7,
        progress_max: int = 12,
    ):
        if reply_token == "local":  # ローカルでのテスト用
            print("Assistant: ", message, end="")
            print(f"({progress} / {progress_max})")
            return
        json_path = self.config["line"]["template_path"]["gpt_response"]
        template = json.load(open(json_path))
        percentage1 = progress / progress_max * 100
        percentage2 = 100 - percentage1
        percentage1 = f"{percentage1:.0f}%"
        percentage2 = f"{percentage2:.0f}%"

        template["body"]["contents"][0]["text"] = session_id
        template["body"]["contents"][1]["contents"][0]["contents"][0][
            "width"
        ] = percentage1
        template["body"]["contents"][1]["contents"][0]["contents"][1][
            "width"
        ] = percentage2
        template["body"]["contents"][2]["contents"][1]["contents"][1]["text"] = message

        response_json = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "flex",
                    "altText": "This is a Flex Message",
                    "contents": template,
                }
            ],
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            raise Exception(response.text)

    def reply_interview_end(self, reply_token: str):
        if reply_token == "local":  # ローカルでのテスト用
            print(
                "Assistant: ",
                "お時間をいただきありがとうございました。インタビューを終了します",
            )
            return
        json_path = self.config["line"]["template_path"]["interview_end"]
        template = json.load(open(json_path))
        response_json = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "flex",
                    "altText": "This is a Flex Message",
                    "contents": template,
                }
            ],
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            raise Exception(response.text)

    def push_gpt_response(
        self,
        line_id: str,
        session_id: str,
        message: str,
        progress: int = 7,
        progress_max: int = 12,
    ):
        json_path = self.config["line"]["template_path"]["gpt_response"]
        template = json.load(open(json_path))

        progress1 = progress / progress_max * 100
        progress2 = 100 - progress1
        progress1 = f"{progress1:.0f}%"
        progress2 = f"{progress2:.0f}%"

        template["body"]["contents"][0]["text"] = session_id
        template["body"]["contents"][1]["contents"][0]["contents"][0][
            "width"
        ] = progress1
        template["body"]["contents"][1]["contents"][0]["contents"][1][
            "width"
        ] = progress2
        template["body"]["contents"][2]["contents"][1]["contents"][1]["text"] = message

        response_json = {
            "to": line_id,
            "messages": [
                {
                    "type": "flex",
                    "altText": "This is a Flex Message",
                    "contents": template,
                }
            ],
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/push",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            raise Exception(response.text)

    def broadcast_flex_message(self, message_json: dict):
        response = requests.post(
            "https://api.line.me/v2/bot/message/broadcast",
            headers=self.headers,
            json={
                "messages": [
                    {
                        "type": "flex",
                        "altText": "インタビューのお知らせ",
                        "contents": message_json,
                    }
                ]
            },
        )
        if response.status_code != 200:
            raise Exception(response.text)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    line_client = line(channel_access_token)
    line_client.broadcast_flex_message(
        json.load(open("templates/broadcast_message.json"))
    )
