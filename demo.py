import os

import openai
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# 環境変数からAPIキーを取得
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI APIキーを設定
openai.api_key = api_key

prompt = input("user: ")

response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "you are a helpful assistant.",
        },
        {"role": "user", "content": prompt},
    ],
)
print("assistant: ", response.choices[0].message.content)
print("assistant: ", response.choices[0].message.content)
