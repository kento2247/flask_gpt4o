import openai
from dotenv import load_dotenv
import os

load_dotenv()
# OpenAI APIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")


# GPTを使って回答に特定の要素が含まれているかを判断する関数
def gpt_judge(answer, focus):
    # 判断基準をより具体的に
    if focus == "日常的な作業か頻度":
        prompt = f"""
        以下の回答には、日常的な作業や頻度に関する情報が含まれていますか？
        例えば、毎日行っている、定期的に行っている、習慣的に行っているなどの情報が述べられていますか？
        Yes/Noで答えてください。

        回答: {answer}
        """
    if focus == "目的や目標":
        prompt = f"""
        以下の回答には、目的や目標に関する情報が含まれていますか？ 
        目的や目標という言葉が入っていたり、何のために行動しているかが述べられていますか？
        Yes/Noで答えてください。
        
        回答: {answer}
        """
    elif focus == "気付きや発見":
        prompt = f"""
        以下の回答には、気付きや発見に関する情報が含まれていますか？
        例えば、思ったこと、感じたこと、見たこと、聞いたこと、など認知的に気が付いたことが述べられていますか？
        Yes/Noで答えてください。
        
        回答: {answer}
        """
    elif focus == "時間的なプレッシャー":
        prompt = f"""
        以下の回答には、時間的なプレッシャーに関する情報が含まれていますか？
        例えば、時間的なプレッシャーがあるなどの情報が述べられていますか？
        Yes/Noで答えてください。
        
        回答: {answer}
        """
    elif focus == "経験":
        prompt = f"""
        以下の回答には、経験というキーワードや要素が含まれていますか？
        例えば、過去の経験を参考しているなどの情報が述べられていますか？
        Yes/Noで答えてください。
        
        回答: {answer}
        """

    else:
        # 他の要素に関しては一般的な判断
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
    あなたはインタビュアーです。以下の文脈と焦点に基づいて、インタビューで使用する**1つの質問**を日本語で生成してください。説明文は不要です、質問だけを生成してください。ただし、インタビュー技法やプロービング、アクティブリスニングなどを用いて効果的に心理を探求する質問を生成してください。
    
    文脈: {context}
    焦点: {focus}
    
    質問のみを生成してください。
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # gpt-4oモデルを使用
        messages=[
            {
                "role": "system",
                "content": "あなたは日本語でインタビューの質問を作成するアシスタントです。インタビュー技法やプロービング、アクティブリスニングなどを用いて効果的に心理を探求する質問を生成してください。",
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
            "代替案": None
        }

    def start(self):
        # 最初の質問：今何をしているのですか？
        answer = input("今、何をしているのですか？: ")

        # 優先度1: 日常性の判断
        result = gpt_judge(answer, "日常的な作業か頻度")

        if result == "yes":
            # 日常性として格納
            self.details["日常性"] = answer
            print("日常性に関する情報を格納しました。")
            # 作業内容へ進む
            self.ask_task_content(answer)
        else:
            # 作業内容へ進む
            self.ask_task_content(answer)

    def ask_task_content(self, answer):
        # 作業内容が含まれているかをGPTで判断
        result = gpt_judge(answer, "作業内容")

        if result == "yes":
            # 具体性の判断へ進む
            self.ask_specific_task_content(answer)
        else:
            # 時間的プレッシャーへ進む
            self.ask_time_pressure(answer)

    def ask_specific_task_content(self, answer):
        # 具体的な作業内容が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な作業内容")

        if result == "yes":
            # 具体的な作業内容として格納
            self.details["作業内容"] = answer
            print("具体的な作業内容を格納しました。")
            self.ask_time_pressure(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_task_content()

    def deep_dive_task_content(self):
        # 具体的な作業内容を深掘り（日本語で質問生成）
        context = "相手が作業内容について話していますが、詳細が不足しています。"
        focus = "その作業についてもう少し具体的に教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["作業内容"] = deep_answer
        print("深掘りした作業内容を格納しました。")
        self.ask_time_pressure(deep_answer)

    def ask_time_pressure(self, answer):
        # 時間的プレッシャーが含まれているかをGPTで判断
        result = gpt_judge(answer, "時間的なプレッシャー")

        if result == "yes":
            self.ask_specific_time_pressure(answer)
        else:
            # 気付きへ進む
            self.ask_awareness(answer)

    def ask_specific_time_pressure(self, answer):
        # 具体的な時間的プレッシャーが含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な時間的プレッシャー")

        if result == "yes":
            # 具体的な時間的プレッシャーとして格納
            self.details["時間的プレッシャー"] = answer
            print("具体的な時間的プレッシャーを格納しました。")
            self.ask_awareness(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_time_pressure()

    def deep_dive_time_pressure(self):
        # 時間的プレッシャーについて深掘り（日本語で質問生成）
        context = "相手が時間的プレッシャーについて話していますが、詳細が不足しています。"
        focus = "その時間的なプレッシャーについてもう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["時間的プレッシャー"] = deep_answer
        print("深掘りした時間的プレッシャーを格納しました。")
        self.ask_awareness(deep_answer)

    def ask_awareness(self, answer):
        # 気付きが含まれているかをGPTで判断
        result = gpt_judge(answer, "気付きや発見")

        if result == "yes":
            self.ask_specific_awareness(answer)
        else:
            # 目的・目標へ進む
            self.ask_goals(answer)

    def ask_specific_awareness(self, answer):
        # 気付きに関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な気付きや発見")

        if result == "yes":
            # 具体的な気付きとして格納
            self.details["気付き"] = answer
            print("気付きに関する情報を格納しました。")
            self.ask_goals(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_awareness()

    def deep_dive_awareness(self):
        # 気付きについて深掘り（日本語で質問生成）
        context = "相手が作業中の気付きについて話していますが、詳細が不足しています。"
        focus = "その作業中の気付きについてもう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["気付き"] = deep_answer
        print("深掘りした気付きに関する情報を格納しました。")
        self.ask_goals(deep_answer)

    def ask_goals(self, answer):
        # 目的や目標が含まれているかをGPTで判断
        result = gpt_judge(answer, "目的や目標")

        if result == "yes":
            self.ask_specific_goals(answer)
        else:
            # 次のステップへ進む
            print("目的や目標の情報は含まれていません。次に進みます。")
            self.ask_prediction(answer)

    def ask_specific_goals(self, answer):
        # 目的や目標に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な目的や目標")

        if result == "yes":
            # 具体的な目的や目標として格納
            self.details["目的・目標"] = answer
            print("目的・目標に関する情報を格納しました。")
            self.ask_prediction(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_goals()

    def deep_dive_goals(self):
        # 目的や目標について深掘り（日本語で質問生成）
        context = "相手が作業の目的や目標について話していますが、詳細が不足しています。"
        focus = "その作業の目的や目標についてもう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["目的・目標"] = deep_answer
        print("深掘りした目的や目標に関する情報を格納しました。")
        self.ask_prediction(deep_answer)

    def ask_prediction(self, answer):
        # 事象予測が含まれているかをGPTで判断
        result = gpt_judge(answer, "事象予測")

        if result == "yes":
            self.ask_specific_prediction(answer)
        else:
            # 知識へ進む
            self.ask_knowledge(answer)

    def ask_specific_prediction(self, answer):
        # 事象予測に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な事象予測")

        if result == "yes":
            # 具体的な事象予測として格納
            self.details["事象予測"] = answer
            print("事象予測に関する情報を格納しました。")
            self.ask_knowledge(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_prediction()

    def deep_dive_prediction(self):
        # 事象予測について深掘り（日本語で質問生成）
        context = "相手が今後の事象予測について話していますが、詳細が不足しています。"
        focus = (
            "今後の事象についてどのように予測しているか、もう少し詳しく教えてください。"
        )
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["事象予測"] = deep_answer
        print("深掘りした事象予測に関する情報を格納しました。")
        self.ask_knowledge(deep_answer)

    def ask_knowledge(self, answer):
        # 知識が含まれているかをGPTで判断
        result = gpt_judge(answer, "知識")

        if result == "yes":
            self.ask_specific_knowledge(answer)
        else:
            # 経験へ進む
            self.ask_experience(answer)

    def ask_specific_knowledge(self, answer):
        # 知識に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な知識")

        if result == "yes":
            # 具体的な知識として格納
            self.details["知識"] = answer
            print("知識に関する情報を格納しました。")
            self.ask_experience(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_knowledge()

    def deep_dive_knowledge(self):
        # 知識について深掘り（日本語で質問生成）
        context = "相手が特定の知識について話していますが、詳細が不足しています。"
        focus = "どのような知識が関連しているのか、もう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["知識"] = deep_answer
        print("深掘りした知識に関する情報を格納しました。")
        self.ask_experience(deep_answer)

    def ask_experience(self, answer):
        # 経験が含まれているかをGPTで判断
        result = gpt_judge(answer, "経験")

        if result == "yes":
            self.ask_specific_experience(answer)
        else:
            # 根拠へ進む
            self.ask_basis(answer)

    def ask_specific_experience(self, answer):
        # 経験に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な経験")

        if result == "yes":
            # 具体的な経験として格納
            self.details["過去の経験"] = answer
            print("経験に関する情報を格納しました。")
            self.ask_basis(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_experience()

    def deep_dive_experience(self):
        # 経験について深掘り（日本語で質問生成）
        context = "相手が過去の経験について話していますが、詳細が不足しています。"
        focus = "これまでの経験に基づいて、もう少し具体的に教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["過去の経験"] = deep_answer
        print("深掘りした経験に関する情報を格納しました。")
        self.ask_basis(deep_answer)

    def ask_basis(self, answer):
        # 根拠が含まれているかをGPTで判断
        result = gpt_judge(answer, "根拠")

        if result == "yes":
            self.ask_specific_basis(answer)
        else:
            # 代替案へ進む
            self.ask_alternative(answer)

    def ask_specific_basis(self, answer):
        # 根拠に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な根拠")

        if result == "yes":
            # 具体的な根拠として格納
            self.details["根拠"] = answer
            print("根拠に関する情報を格納しました。")
            self.ask_alternative(answer)
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_basis()

    def deep_dive_basis(self):
        # 根拠について深掘り（日本語で質問生成）
        context = "相手が行動の根拠について話していますが、詳細が不足しています。"
        focus = "その根拠について、もう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["根拠"] = deep_answer
        print("深掘りした根拠に関する情報を格納しました。")
        self.ask_alternative(deep_answer)

    def ask_alternative(self, answer):
        # 代替案が含まれているかをGPTで判断
        result = gpt_judge(answer, "代替案")

        if result == "yes":
            self.ask_specific_alternative(answer)
        else:
            print("全ての項目が終了しました。")
            # second_phaseへ進む
            self.second_phase()

    def ask_specific_alternative(self, answer):
        # 代替案に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な代替案")

        if result == "yes":
            # 具体的な代替案として格納
            self.details["代替案"] = answer
            print("代替案に関する情報を格納しました。")
            self.second_phase()
        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_alternative()

    def deep_dive_alternative(self):
        # 代替案について深掘り（日本語で質問生成）
        context = "相手が代替案について話していますが、詳細が不足しています。"
        focus = "他にどのような方法があるか、もう少し詳しく教えてください。"
        dynamic_question = generate_dynamic_question(context, focus)
        deep_answer = input(dynamic_question)
        self.details["代替案"] = deep_answer
        print("深掘りした代替案に関する情報を格納しました。")
        self.second_phase()

    def show_details(self):
        # 格納された情報を表示
        print("\n格納された情報:")
        for key, value in self.details.items():
            if value:
                print(f"{key}: {value}")
            else:
                print(f"{key}: 未格納")

    # 第二段階: detailの確認に基づいて質問を行うフェーズ
    def second_phase(self):
        # 優先度1: 日常性の情報が埋まっているか確認
        if self.details["日常性"]:
            # 日常性の情報が埋まっているので次へ進む
            print("日常性の情報はすでに格納されています。次のステップへ進みます。")
            self.check_task_content_detail()
        else:
            # 日常性について再度質問（プロンプトを日本語で生成）
            context = "相手はまだその作業がどれくらいの頻度で行われるか話していません。"
            focus = "その作業がどれくらいの頻度で行われるかを尋ねてください。"
            dynamic_question = generate_dynamic_question(context, focus)
            deep_answer = input(dynamic_question)
            self.details["日常性"] = deep_answer
            print("日常性の詳細を格納しました。")
            self.check_task_content_detail()

    def check_task_content_detail(self):
        # 作業内容の情報が埋まっているか確認
        if self.details["作業内容"]:
            print("作業内容の情報はすでに格納されています。次のステップへ進みます。")
        else:
            # 作業内容について再度質問（プロンプトを日本語で生成）
            context = "相手はまだ具体的な作業内容を話していません。"
            focus = "その作業内容について尋ねてください。"
            dynamic_question = generate_dynamic_question(context, focus)
            deep_answer = input(dynamic_question)

            # gpt_judgeで作業内容が含まれているか確認
            prompt = f"この回答は具体的な作業内容を含んでいますか？ Yes/No: '{deep_answer}'"
            result = gpt_judge(deep_answer, "具体的な作業内容")

            if result == "yes":
                self.details["作業内容"] = deep_answer
                print("作業内容の情報を格納しました。")
            else:
                # さらに深掘りして質問
                self.deep_dive_task_content()

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
