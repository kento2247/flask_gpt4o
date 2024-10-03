import requests
import json
import openai
from dotenv import load_dotenv
import os
from src.mongodb import mongodb


class Summerizer:
    def __init__(self, config: dict):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.config = config

    def summerize(self, messages: list, try_num: int = 10) -> dict:
        interview_data = json.dumps(messages)

        # プロンプトの定義
        prompt = (
            interview_data
            + "\nこのインタビューデータから、タスクにおける意思決定の認知プロセスを明らかにする認知タスク分析を行いたいです。"
            "そのため、以下の内容を要約してください。ひとつもなかったり、複数の内容が一つの項目にあっても構いません。\n"
            "1. 行動（内容、手順、日常性、時間的圧力など）\n"
            "2. 認知（気づき、感じたこと、手がかり、目標、可能性や必要性など）\n"
            "3. 情報（用いた経験や知識など）\n\n"
            "ただし、行動と認知と情報の要素の抽出も、以下のインタビューの目的やプローブを理解しながら行ってほしい。\n"
            "インタビューにおける指示は以下である。\n\n"
            "あなたはプラントの現場を取材するプロのインタビュアーです．以下の内容に基づいて、従業員に対してインタビューを行ってください。 \n"
            "インタビューは、認知タスク分析を行うためのものです。つまり、リアルタイムで従業員が取り組んでいるタスクにおける、認知プロセスを理解するためのデータをインタビューで集めることが目的です。\n"
            "認知タスク分析とは、熟練者や専門家が、タスクにおいて意識的、あるいは無意識的におこなう意思決定の認知プロセスを探るための手法です。\n"
            "インタビューでは、認知プロセスにおける**情報**と**認知**と**行動**について質問をしてください。\n"
            "ただし、RPDに基づき、また効果的に情報を引き出すために、CDM（Cognitive Dimensions of Notations）におけるプローブの手法や、"
            "インタビュー技法や心理学を用いてください。以下にそれぞれの説明をします。\n\n"
            "RPDは、人々が経験をどのように活用して意思決定を行うかを説明する認知モデルです。その内容は以下の通りです。\n"
            "1. 状況を典型的な経験に当てはめる\n"
            "2. その時に目標や手がかり、可能性などを認識する\n"
            "3. うまくいきそうな行動を選択する\n"
            "4. うまくいくかどうかを頭の中でシミュレーションする\n"
            "5. 行動を実行する\n"
            "CDM（Cognitive Dimensions of Notations）は、認知タスク分析の枠組みにおける、過去に発生した非日常的な事象に対して、"
            "専門家の判断や意思決定の側面を引き出すための回顧的なインタビュー手法です。しかし、今回は非日常的ではなく日常的な状況で行なわれているタスクを対象としたインタビューに用います。\n"
            "CDMにおけるプローブは、以下のようなものがあります。\n"
            "手がかり: 何を見て、聞いて、感じていたか？\n"
            "知識: この意思決定で使用した情報は何か？その情報はどのようにして得たのか？\n"
            "類似経験: 過去の経験を思い出したか？\n"
            "目標: その時の具体的な目標は何か？\n"
            "選択肢: 他にどのような行動の選択肢が考えられたか？\n"
            "根拠: どのようにしてこの選択肢が選ばれたのか？他の選択肢が拒否された理由は？何か規則があったか？\n"
            "経験: この意思決定を行う上で、どのような経験が必要だったか？\n"
            "支援: この意思決定が最善ではなかった場合、どのような知識、情報が役立ったか？\n"
            "時間的圧力: この意思決定にはどの程度の時間的圧力がかかっていたか？\n\n"
            "そして結果は、jsonで出力してください。出力の見本としては、以下の形です。\n"
            "{\n"
            '"action": {\n'
            '    "monitoring": "モニターの監視を行い、異常がないかどうかの確認。",\n'
            '    "comparison": "画面の情報を見比べて、赤い警告表示がないか探索。"\n'
            "},\n"
            '"recognition": {\n'
            '    "threat_awareness": "赤い警告表示を見つけたとき、プラントの安全が脅かされていると感じる。",\n'
            '    "emotional_response": "異常を発見した際に焦りを感じるが、冷静に対応しなければならないと理解している。"\n'
            "},\n"
            '"information": {\n'
            '    "sources": "安全マニュアル、先輩の教え、過去のシミュレーションの経験。",\n'
            '    "critical_knowledge": "プラントの稼働停止手順や警告の対処方法。"\n'
            "}\n"
            "}\n"
        )

        # リクエストヘッダーとペイロードの設定
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.2,
        }

        for _ in range(try_num):
            # APIリクエストの送信
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )

            if response.status_code != 200:
                print("エラー:", response.status_code, response.text)
                break

            result = response.json()
            extracted_data = result["choices"][0]["message"]["content"]

            try:
                extracted_data = json.loads(extracted_data)
                return extracted_data
            except json.JSONDecodeError:
                print("JSON形式に変換できませんでした。再試行します。")
                continue

    def get_messages_list_db(self) -> list:
        # mongodb接続設定
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_database_name = self.config["mongodb"]["database_name"]
        mongodb_collection_name = self.config["mongodb"]["collection_name"]
        mongo_db_client = mongodb(
            username=mongodb_username,
            password=mongodb_password,
            database_name=mongodb_database_name,
            collection_name=mongodb_collection_name,
        )

        all_messages = mongo_db_client.all_messages()
        return all_messages

    def get_messages_list_local(
        self, messages_path: str = "../tmp/messages.json"
    ) -> list:
        with open(messages_path, "r") as f:
            messages = json.load(f)

        return [{"data": messages}]  # ここで返すデータの形式を変更する
