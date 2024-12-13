import openai
from dotenv import load_dotenv
import os

load_dotenv()
# OpenAI APIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")


# GPTを使って回答に特定の要素が含まれているかを判断する関数
def gpt_judge(answer, focus):
    # 各要素に対する判定プロンプトを生成
    prompt = f"""
    以下の回答には、{focus}に関する情報が含まれていますか？
    Yes/Noで答えてください。

    回答: {answer}
    """

    # OpenAI APIコールで判断
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # gpt-4oモデルを使用
        messages=[
            {
                "role": "system",
                "content": "あなたはインタビューの回答を分析するアシスタントです。",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # GPTの判断結果を返す
    return response["choices"][0]["message"]["content"].strip().lower()


# GPTを使って次の質問を生成する関数（深掘りや第二段階で使用）
def generate_dynamic_question(context, focus):
    prompt = f"""
    あなたはインタビュアーです。以下の文脈と焦点に基づいて、インタビューで使用する**1つの質問**を日本語で生成してください。説明文は不要です、質問だけを生成してください。インタビュー技法やプロービングを用いて、認知タスク分析における情報収集を意識してください。
    
    文脈: {context}
    焦点: {focus}
    
    
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # gpt-4oモデルを使用
        messages=[
            {
                "role": "system",
                "content": "あなたは日本語でインタビューの質問を作成するアシスタントです。インタビュー技法やプロービングを用いて、認知タスク分析における情報収集を意識してください。",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"].strip()


# インタビューのフローを管理するクラス
class InterviewFlowGPT:
    def __init__(self):
        # detailに格納する情報を保持する辞書
        self.details = {
            "日常性": None,
            "作業内容": None,
            "時間的プレッシャー": None,
            "気付き": None,
            "目的・目標": None,
            "事象予測": None,
            "知識": None,
            "過去の経験": None,
            "根拠": None,
            "代替案": None,
        }
        self.answer_first = None  # 最初の回答を保持するための変数

    def start(self):
        # 最初の質問：今何をしているのですか？
        self.answer_first = input("今、何をしているのですか？: ")

        # 各要素が含まれているかをチェック
        self.check_all_elements(self.answer_first)

    def check_all_elements(self, answer):
        # 各要素に関する判定を行う
        elements_to_check = {
            "日常性": "日常的な作業か頻度",
            "作業内容": "作業内容",
            "時間的プレッシャー": "時間的なプレッシャー",
            "気付き": "気付きや発見",
            "目的・目標": "目的や目標",
            "事象予測": "事象予測",
            "知識": "知識",
            "過去の経験": "経験",
            "根拠": "根拠",
            "代替案": "代替案",
        }

        # 各要素をGPTに判断させ、含まれていたらその要素について掘り下げる
        found_element = False  # 少なくとも1つ要素が見つかったかどうかを追跡
        for key, focus in elements_to_check.items():
            result = gpt_judge(answer, focus)
            if result == "yes":
                self.details[key] = answer
                print(f"{key}に関する情報を格納しました。")
                found_element = True
                # 見つかった要素に基づいて掘り下げる質問を生成
                self.deep_dive_element(key)
        #全ての要素のチェックが終わったら、second_phaseに進む
        self.second_phase()

        # もし何も要素が見つからなければ second_phase に進む
        if not found_element:
            self.second_phase()

    def deep_dive_element(self, element):
        # 特定の要素に関してさらに深掘りする
        context = f"相手が{element}に関して話していますが、詳細が不足しています。"
        focus = f"その{element}についてもう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details[element] = deep_answer
        print(f"深掘りした{element}に関する情報を格納しました。")

    def second_phase(self):
        # second_phaseに進むため、次の質問を生成して詳細を確認
        print("第二段階に移行します。")
        # 例：日常性が埋まっていなければ質問を生成
        if self.details["日常性"] is None:
            context = "相手はまだ日常的にその作業を行っているかどうか話していません。"
            focus = "その作業がどれくらいの頻度で行われるかを尋ねてください。"
            dynamic_question = generate_dynamic_question(context, focus)
            deep_answer = input(dynamic_question)
            self.details["日常性"] = deep_answer
            print("日常性の詳細を格納しました。")

        # 作業内容や他の要素についても同様に処理
        if self.details["作業内容"] is None:
            context = "相手はまだ具体的な作業内容を話していません。"
            focus = "その作業内容について教えてください。"
            dynamic_question = generate_dynamic_question(context, focus)
            deep_answer = input(dynamic_question)
            self.details["作業内容"] = deep_answer
            print("作業内容の詳細を格納しました。")

        # 他の要素についても同様に処理を進める

    def show_details(self):
        # 格納された情報を表示
        print("\n格納された情報:")
        for key, value in self.details.items():
            if value:
                print(f"{key}: {value}")
            else:
                print(f"{key}: 未格納")


# インタビューの流れを開始
flow_gpt = InterviewFlowGPT()
flow_gpt.start()

# 格納された情報を表示
flow_gpt.show_details()
