import argparse
import os

import openai
from dotenv import load_dotenv


def main():
    # 環境変数からAPIキーを取得
    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        # {
        #     "role": "system",
        #     "content": "あなたは職場を取材するインタビュアーです．行動の背景要因や思いの深層を嫌がられずに聞き出すことが目的です．チャットを開始してください．長文を送らないように気をつけること．",
        # }
        {
            "role": "system",
            "content": "あなたは化学プラント現場におけるインタビュアーです．現場の安全性や効率性を向上させるための情報を収集することが目的です．チャットを開始してください．質問文は一文のみにすること．",
        }
    ]
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    print("assistant: ", response.choices[0].message.content)

    while True:
        prompt = input("user: ")
        if prompt == "exit":
            break
        messages.append({"role": "user", "content": prompt})
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        print("assistant: ", response.choices[0].message.content)
        messages.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--load_env",
        action="store_true",
        help="Load environment variables from .env file",
    )
    args = parser.parse_args()
    if args.load_env:
        load_dotenv()
    main()
