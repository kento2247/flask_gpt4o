import argparse
import os

import openai
from dotenv import load_dotenv


def main():
    # 環境変数からAPIキーを取得
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print("API key:", openai.api_key)
    messages = [
        {
            "role": "system",
            "content": "あなたは職場を取材するインタビュアーです．CDMの手法を用いて、日常のうまくいっている業務と、同じ業務に関して事故やヒヤリハットなどの経験の2つの業務の側面の違いを抽出したいです。チャットを開始してください．長文を送らないように気をつけること．",
        }
        # {
        #     "role": "system",
        #     "content": "あなたは化学プラント現場におけるインタビュアーです．現場の安全性や効率性を向上させるための情報を収集することが目的です．このインタビューデータを使って、社会技術システムにおける機能共鳴分析であるFRAMを行うために、作業者の業務内容を、特定の目的を果たすための機能に時系列に沿って分解し、それぞれの機能に対して六つの側面として、Time ：機能の実行に影響を及ぼす時間の条件 、Control： 機能を実行する際の制約条件 機能名 目的を達成するために必要な活動 、Input ：機能を実行するための必要条件、Output ：機能を通して得られた結果（次の機能のInputになる）、Preconditions： 機能を実行する前に必要となる前提条件 、Resource： 機能の実行に必要な資源、を抽出することが目的です。最終的にはこれを、現場のシステム全体に広げて安全性を評価します。それでは、チャットを開始してください．質問文は一文のみにすること．",
        # }
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
        print("Loaded environment variables from .env file")
    main()
