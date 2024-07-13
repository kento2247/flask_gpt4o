import json

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

    def reply(self, reply_token: str, message: str):
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
            print(response.text)

    def get_profile(self, user_id: str) -> dict:
        response = requests.get(
            f"https://api.line.me/v2/bot/profile/{user_id}",
            headers=self.headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(response.text)
            return {}

    def reply_gpt_response(self, reply_token: str, session_id: str, message: str):
        json_path = self.config["line"]["template_path"]["gpt_response"]
        template = json.load(open(json_path))
        template["body"]["contents"][0]["text"] = session_id
        template["body"]["contents"][1]["contents"][1]["contents"][1]["text"] = message

        return template
        # response_json = {
        #     "replyToken": reply_token,
        #     "messages": template,
        # }
        # response = requests.post(
        #     "https://api.line.me/v2/bot/message/reply",
        #     headers=self.headers,
        #     json=response_json,
        # )
        # if response.status_code != 200:
        #     print(response.text)

    def reply_interview_end(self, reply_token: str):
        json_path = self.config["line"]["template_path"]["interview_end"]
        template = json.load(open(json_path))
        response_json = {
            "replyToken": reply_token,
            "messages": template,
        }
        response = requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=self.headers,
            json=response_json,
        )
        if response.status_code != 200:
            print(response.text)
