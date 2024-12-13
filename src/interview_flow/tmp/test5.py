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
def generate_dynamic_question(history, focus):
    # インタビュー履歴をプロンプトに追加して、次に聞くべき質問を生成
    history_text = "\n".join(
        [f"質問: {h['question']} 回答: {h['answer']}" for h in history]
    )
    prompt = f"""
    あなたはインタビュアーです。以下のこれまでのインタビュー履歴に基づいて、インタビューで使用する**1つの質問**を日本語で生成してください。
    質問は、これまでのインタビューの流れを考慮し、回答者が深く考えたり、さらなる情報を提供できるように「{focus}」について適切に聞いてください。
    説明文は不要です。質問のみを生成してください。
    
    これまでのインタビュー履歴:
    {history_text}
    
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # gpt-4oモデルを使用
        messages=[
            {
                "role": "system",
                "content": (
                    "あなたはプラントの現場を取材するプロのインタビュアーです。以下の内容に基づいて、従業員に対してインタビューを行ってください。"
                    "インタビューは、認知タスク分析を行うためのものです。つまり、リアルタイムで従業員が取り組んでいるタスクにおける、"
                    "認知プロセスを理解するためのデータをインタビューで集めることが目的です。\n\n"
                    "認知タスク分析とは、熟練者や専門家が、タスクにおいて意識的、あるいは無意識的におこなう意思決定の認知プロセスを探るための手法です。\n"
                    "インタビューでは、認知プロセスにおける**情報**と**認知**と**行動**について質問をしてください。\n"
                    "ただし、RPDに基づき、また効果的に情報を引き出すために、CDM（Cognitive Dimensions of Notations）におけるプローブの手法や、"
                    "インタビュー技法や心理学を用いてください。以下にそれぞれの説明をします。\n\n"
                    "RPDは、人々が経験をどのように活用して意思決定を行うかを説明する認知モデルです。その内容は以下の通りです。\n"
                    "1. 状況を典型的な経験に当てはめる\n"
                    "2. その時に目標や手がかり、可能性などを認識する\n"
                    "3. うまくいきそうな行動を選択する\n"
                    "4. うまくいくかどうかを頭の中でシミュレーションする\n"
                    "5. 行動を実行する\n\n"
                    "CDM（Cognitive Dimensions of Notations）は、認知タスク分析の枠組みにおける、過去に発生した非日常的な事象に対して、"
                    "専門家の判断や意思決定の側面を引き出すための回顧的なインタビュー手法です。しかし、今回は非日常的ではなく日常的な状況で"
                    "行なわれているタスクを対象としたインタビューに用います。\n"
                    "CDMにおけるプローブは、以下のようなものがあります。\n\n"
                    "手がかり: 何を見て、聞いて、感じていたか？\n"
                    "知識: この意思決定で使用した情報は何か？その情報はどのようにして得たのか？\n"
                    "類似経験: 過去の経験を思い出したか？\n"
                    "目標: その時の具体的な目標は何か？\n"
                    "選択肢: 他にどのような行動の選択肢が考えられたか？\n"
                    "根拠: どのようにしてこの選択肢が選ばれたのか？他の選択肢が拒否された理由は？何か規則があったか？\n"
                    "経験: この意思決定を行う上で、どのような経験が必要だったか？\n"
                    "支援: この意思決定が最善ではなかった場合、どのような知識、情報が役立ったか？\n"
                    "時間的圧力: この意思決定にはどの程度の時間的圧力がかかっていたか？\n\n"
                    "インタビュー技法に関して、インタビューにおいて、本人が自意識的に取り組んでいないような隠れた認知を取り出すためには、"
                    "柔軟で自然な会話を通して相手から効果的に情報を引き出すための工夫が必要になります。\n"
                    "意識して欲しい技法は以下です。\n"
                    "1. オープンクエスチョンとクローズドクエスチョンのバランスを取ること\n"
                    "2. フォローアップ質問をすること\n"
                    "3. リフレクティブリスニングをすること。例:「その状況は難しそうですが、実際にはどうでしょうか？」\n"
                    "4. 適度にインタビュアーとしての意見や推論を言うこと。例:「過去に何か教訓を得た経験があったから、そうやっているのでしょうか？」\n\n"
                    "最後に、以下の認知タスク分析におけるインタビュー手順に従ってください。\n"
                    "1. 最初の質問は、「今、何の作業をしているのですか？」という質問にすること\n"
                    "2. 回答者が行っている作業について、行動の側面を抽象的に聞き出した後、CDMを用いて日常性や行動の内容、時間的圧力の有無などを簡潔に聞き出す。\n"
                    "3. 回答者が行っている作業について、認知の側面を抽象的に聞き出した後、CDMを用いて具体的に、感じたことや考えたこと、気付いたこと、"
                    "事象予測、目標、行動の選択肢などを簡潔に聞き出す。\n"
                    "4. 回答者が行っている作業について、情報の側面を抽象的に聞き出し、情報の取得方法、情報の内容、経験や知識の有無などを簡潔に聞き出す。\n\n"
                    "ただし、制約は、以下の通りです。\n"
                    "1. 質問は一回につき最大一個にしてください。簡単な相槌はうって構いません。\n"
                    "2. インタビュー技法を意識すること。\n"
                    "3. 同じ質問をしないでください。つまり、行動と認知と情報に関して全体的に、簡潔に取り出すのでよい。\n"
                    "4. 一回の質問に対して、フォローアップ質問は最大3回です。\n"
                    "5. CDMのプローブはそのまま使わず、文脈に合わせて単語や言い回しを変えてください。\n\n"
                    "それでは、チャットを開始してください。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"].strip()


class InterviewFlowGPT:
    def __init__(self):
        # 会話履歴を保存するリスト
        self.history = []
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

    def add_to_history(self, question, answer):
        """
        質問と回答を履歴に追加するメソッド
        :param question: 生成した質問
        :param answer: インタビュー対象者からの回答
        """
        self.history.append({"question": question, "answer": answer})

    def generate_initial_question(self, focus):
        """
        インタビューの各段階で使用する初期質問を生成するメソッド
        :param focus: 生成する質問の焦点（例: 行動、認知、知識や経験）
        """
        history_text = "\n".join(
            [f"質問: {h['question']} 回答: {h['answer']}" for h in self.history]
        )
        prompt = f"""
        あなたはインタビュアーです。以下のこれまでのインタビュー履歴に基づいて、インタビューの最初に使用する**1つの質問**を日本語で生成してください。
        質問は、回答者が「{focus}」の要素について話せるような質問を生成してください。
        例えば、行動に焦点を当てる場合は、どのように作業を進めているかを尋ねる質問にしてください。認知の場合は、何を意識しているのか、考えているのかを尋ねてください。
        説明文は不要です。質問のみを生成してください。

        これまでのインタビュー履歴:
        {history_text}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたはプロのインタビュアーです。"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()

    def start_phase_one(self):
        # 第一段階：行動に焦点を当てた質問を生成
        question = self.generate_initial_question("行動の要素")
        answer = input(question)  # 生成した質問を使って回答を取得
        self.add_to_history(question, answer)
        self.process_common_steps(answer)
        self.second_phase_one()  # 第一段階の質問確認フェーズに進む

    def start_phase_two(self):
        # 第二段階：認知に焦点を当てた質問を生成
        question = self.generate_initial_question("認知の要素")
        answer = input(question)  # 生成した質問を使って回答を取得
        self.add_to_history(question, answer)
        self.process_common_steps(answer)
        self.second_phase_two()  # 第二段階の質問確認フェーズに進む

    def start_phase_three(self):
        # 第三段階：知識や経験に焦点を当てた質問を生成
        question = self.generate_initial_question("知識や経験の要素")
        answer = input(question)  # 生成した質問を使って回答を取得
        self.add_to_history(question, answer)
        self.process_common_steps(answer)
        self.second_phase_three()  # 第三段階の質問確認フェーズに進む

    # def start_phase_four(self):
    #     # 第四段階の最初の質問
    #     answer = input("うまくいきそうですか？: ")
    #     self.process_common_steps(answer)
    #     self.second_phase_four()  # 第四段階の質問確認フェーズに進む

    def process_common_steps(self, answer):
        # 日常性の判断
        result = gpt_judge(answer, "日常的な作業か頻度")
        if result == "yes":
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
        # 具体的な作業内容を深掘り（履歴参照）
        focus = "作業内容"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な時間的プレッシャーを深掘り（履歴参照）
        focus = "時間的プレッシャー"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な気付きを深掘り（履歴参照）
        focus = "気付きや発見"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な目的や目標を深掘り（履歴参照）
        focus = "目的や目標"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な事象予測について深掘り（履歴参照）
        focus = "予測や可能性"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
        self.details["予測や可能性"] = deep_answer
        print("深掘りした予測や可能性に関する情報を格納しました。")
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
        # 具体的な知識について深掘り（履歴参照）
        focus = "知識"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な経験について深掘り（履歴参照）
        focus = "経験"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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
        # 具体的な根拠について深掘り（履歴参照）
        focus = "根拠"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
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

    def ask_specific_alternative(self, answer):
        # 代替案に関する具体的な情報が含まれているかをGPTで判断
        result = gpt_judge(answer, "具体的な代替案")

        if result == "yes":
            # 具体的な代替案として格納
            self.details["代替案"] = answer
            print("代替案に関する情報を格納しました。")

        else:
            # 深掘りして質問（generate_dynamic_questionを使用）
            self.deep_dive_alternative()

    def deep_dive_alternative(self):
        # 具体的な代替案について深掘り（履歴参照）
        focus = "代替案"
        dynamic_question = generate_dynamic_question(self.history, focus)
        deep_answer = input(dynamic_question)
        self.add_to_history(dynamic_question, deep_answer)
        self.details["代替案"] = deep_answer
        print("深掘りした代替案に関する情報を格納しました。")

    # 第一段階の確認フェーズ
    def second_phase_one(self):
        if self.details["日常性"]:
            print("日常性の情報はすでに格納されています。次のステップへ進みます。")
            self.check_task_content_detail()
        else:
            focus = "日常性"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["日常性"] = deep_answer
            print("日常性の情報を格納しました。")
            self.check_task_content_detail()

    def check_task_content_detail(self):
        if self.details["作業内容"]:
            print("作業内容の情報はすでに格納されています。次のステップへ進みます。")
            self.check_time_pressure_detail()
        else:
            focus = "作業内容"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["作業内容"] = deep_answer
            print("作業内容の情報を格納しました。")
            self.check_time_pressure_detail()

    def check_time_pressure_detail(self):
        if self.details["時間的プレッシャー"]:
            print(
                "時間的プレッシャーの情報はすでに格納されています。次のステップへ進みます。"
            )
        else:
            focus = "時間的プレッシャー"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["時間的プレッシャー"] = deep_answer
            print("時間的プレッシャーの情報を格納しました。")

    # 第二段階の確認フェーズ
    def second_phase_two(self):
        if self.details["気付き"]:
            print("気付きの情報はすでに格納されています。次のステップへ進みます。")
            self.check_goal_detail()
        else:
            focus = "気付き"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["気付き"] = deep_answer
            print("気付きの情報を格納しました。")
            self.check_goal_detail()

    def check_goal_detail(self):
        if self.details["目的・目標"]:
            print("目的・目標の情報はすでに格納されています。次のステップへ進みます。")
            self.check_prediction_detail()
        else:
            focus = "目的・目標"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["目的・目標"] = deep_answer
            print("目的・目標の情報を格納しました。")
            self.check_prediction_detail()

    def check_prediction_detail(self):
        if self.details["事象予測"]:
            print(
                "事象予測の情報はすでに格納されています。インタビューが完了しました。"
            )
        else:
            focus = "予測や可能性、必要性"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["事象予測"] = deep_answer
            print("事象予測の情報を格納しました。")

    # 第三段階の確認フェーズ
    def second_phase_three(self):
        if self.details["知識"]:
            print("知識の情報はすでに格納されています。次のステップへ進みます。")
            self.check_experience_detail()
        else:
            focus = "知識"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["知識"] = deep_answer
            print("知識の情報を格納しました。")
            self.check_experience_detail

    def check_experience_detail(self):
        if self.details["過去の経験"]:
            print("経験の情報はすでに格納されています。インタビューが完了しました。")
        else:
            focus = "経験"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["過去の経験"] = deep_answer
            print("経験の情報を格納しました。")

    # 第四段階の確認フェーズ
    def second_phase_four(self):
        if self.details["根拠"]:
            print("根拠の情報はすでに格納されています。次のステップへ進みます。")
            # self.check_alternative_detail()
        else:
            focus = "根拠"
            dynamic_question = generate_dynamic_question(self.history, focus)
            deep_answer = input(dynamic_question)
            self.add_to_history(dynamic_question, deep_answer)
            self.details["根拠"] = deep_answer
            print("根拠の情報を格納しました。")
            # self.check_alternative_detail()

    # def check_alternative_detail(self):
    #     if self.details["代替案"]:
    #         print("代替案の情報はすでに格納されています。インタビューが完了しました。")
    #     else:
    #         context = "相手はまだ具体的な代替案について話していません。"
    #         focus = "その代替案について尋ねてください。"
    #         dynamic_question = generate_dynamic_question(context, focus)
    #         deep_answer = input(dynamic_question)

    #         result = gpt_judge(deep_answer, "具体的な代替案")
    #         if result == "yes":
    #             self.details["代替案"] = deep_answer
    #             print("代替案の情報を格納しました。")
    #         else:
    #             self.deep_dive_alternative()

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
flow_gpt.start_phase_one()  # 第一段階を開始
flow_gpt.start_phase_two()  # 第二段階を開始
flow_gpt.start_phase_three()  # 第三段階を開始
flow_gpt.second_phase_four()  # 第四段階を開始

# 格納された情報を表示
flow_gpt.show_details()
