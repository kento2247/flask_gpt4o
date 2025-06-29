import openai


class InterviewAgents:
    def __init__(self, args):
        self.details = {
            "行動": {},  # 行動に関する回答を蓄積
            "認知": {},  # 認知に関する回答を蓄積
            "情報": {},  # 情報に関する回答を蓄積
        }
        assert args.openai_api_key, "OpenAI APIキーが設定されていません"
        args.model = args.model or "gpt-4o"
        args.max_tokens = args.max_tokens or 100
        args.temperature = args.temperature or 0.5

        openai.api_key = args.openai_api_key
        self.model = args.model
        self.max_tokens = args.max_tokens
        self.temperature = args.temperature

    def _get_gpt_response(self, sys_message: str, usr_message: str) -> str:
        req_messages = [
            {"role": "system", "content": sys_message},
            {"role": "user", "content": usr_message},
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=req_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def generate_question(self, elements, messages, message):
        system_message = f"""
        あなたはプラントの現場を取材するプロのインタビュアーです．以下の内容に基づいて、従業員に対して現在取り組んでいるタスクに関するインタビューを行ってください。
        インタビューは、認知タスク分析を行うためのもので、認知プロセスを理解することが目的です。
        認知タスク分析とは、熟練者や専門家が、タスクにおいて意識的、あるいは無意識的におこなう意思決定の認知プロセスを探るための手法です。
        インタビューでは、作業者の現在のタスクに関する、認知プロセスにおける**情報**と**認知**と**行動**について質問をしてください。\n
        直前の回答{message}とそれまでのインタビューの対話{messages}の文脈で、{elements}を埋めるための質問を生成してください。\n
        ただし、認知プロセスのモデルであるRPDに基づき、また効果的に情報を引き出すために、CDM（Cognitive Dimensions of Notations）におけるプローブの手法を意識してください。
        RPDは、人々が経験をどのように活用して意思決定を行うかを説明する認知モデルです。RPDとCDMの内容は以下の通りです。\n
        1. 状況を典型的な経験に当てはめる \n
        2. その時に目標や手がかり、可能性などを認識する \n
        3. うまくいきそうな行動を選択する \n
        4. うまくいくかどうかを頭の中でシミュレーションする \n
        5. 行動を実行する \n
        CDM（Cognitive Dimensions of Notations）は、認知タスク分析の枠組みにおける、過去に発生した非日常的な事象に対して、専門家の判断や意思決定の側面を引き出すための回顧的なインタビュー手法です。しかし、今回は非日常的ではなく日常的な状況で行なわれているタスクを対象としたインタビューに用います。\n
        CDMにおけるプローブは、以下のようなものがあります。\n
        手がかり":"何を見て、聞いて、感じていたか？
        知識":"この意思決定で使用した情報は何か？その情報はどのようにして得たのか？
        類似経験":"過去の経験を思い出したか？
        目標":"その時の具体的な目標は何か？
        選択肢":"他にどのような行動の選択肢が考えられたか？
        根拠":"どのようにしてこの選択肢が選ばれたのか？他の選択肢が拒否された理由は？何か規則があったか？
        経験":"この意思決定を行う上で、どのような経験が必要だったか？
        支援":"この意思決定が最善ではなかった場合、どのような知識、情報が役立ったか？
        時間的圧力":"この意思決定にはどの程度の時間的圧力がかかっていたか？\n
        
        質問生成における制約は、以下の通りです。\n
        1. 質問は一回につき最大一個にしてください。簡単な相槌はうってください。\n
        2. 重複した質問を避けてください・\n
        3. 回答者の現在のタスクに関する質問のみを生成してください\n
        4. 具体的な内容まで深堀を行ってください。\n
        5. CDMのプローブはそのまま使わず、文脈に合わせて単語や言い回しを変えてください。\n
        
        最後に、以下のインタビュー手順に従ってください。\n
        1. 最初の回答で得られた、回答者の現在のタスクに関しての「行動」「認知」「情報」の側面を簡潔に引き出す。行動は日常性や内容、時間的圧力などで、認知は気付きや手がかり、目標などで、情報はもとにした知識や経験についてである。\n
        2. {elements}のインタビュー項目が簡潔にカバーできたら、インタビューを終了する。\n
        
        それでは、チャットを開始してください。
        """

        prompt = f"""
        それまでのインタビューの対話{messages}と直前の回答である{message}を参照し、簡単な相槌と質問を生成してください。
        {elements}が簡潔にカバーできたら、インタビューを終了してください。
        ただし必ず、最初の回答で得られた回答者の現在のタスクに関しての「行動」「認知」「情報」の側面に焦点を当ててください。
        """

        return self._get_gpt_response(system_message, prompt)

    def check_if_interview_should_end(self, messages, elements):
        system_message = """
        あなたはインタビューの終了を判定する役割を持っています。
        メッセージ履歴と引き出された側面に基づき、現在の回答者のタスクに関する**「行動」「認知」「情報」の各側面についての具体的な回答**が全て引き出されているかを厳しく判断し、引き出されている場合のみ終了してください。
        インタビューを終了すべきであれば「終了」とだけ返してください。
        """
        prompt = f"""
        メッセージ履歴:
        {messages}
        引き出された「行動」と「認知」と「情報」：
        {elements}
        

        インタビューは終了すべきですか？メッセージ履歴と引き出された「行動」と「認知」と「情報」を参照し、現在のタスクについて行動、認知、情報の具体的な回答が取得できている場合のみ終了してください。少なくとも、各側面についての回答が1個以上取得できていることを確認してください。
        """

        return "終了" in self._get_gpt_response(system_message, prompt)

    def extract_elements(self, message, messages):
        system_message = """
        あなたは認知タスク分析の専門家です。
        最新の回答が「行動」「認知」「情報」のどのカテゴリに該当するかを判断し、そのカテゴリ名を明示的に返答してください。
        例えば、回答が行動に関連する場合、「行動」とだけ出力してください。
        """

        prompt = f"""
        最新の回答: {message}
        メッセージ履歴:
        {messages}

        最新の回答がどのカテゴリ（行動、認知、情報）に該当するかを明確に示してください。行動は日常性や内容、時間的圧力などの情報が含まれ、認知は気付きや手がかり、選択肢や目標などの情報が含まれ、情報は、行動において用いる知識や経験などの参考にしていることが含まれます。カテゴリ名のみを出力してください。
        """

        updated_category = self._get_gpt_response(system_message, prompt).strip()

        self._add_to_details(updated_category, message)

        elements = {
            "行動": self.details["行動"],
            "認知": self.details["認知"],
            "情報": self.details["情報"],
        }
        return elements

    def _add_to_details(self, category, message):
        if category in self.details:
            key = f"entry_{len(self.details[category]) + 1}"
            self.details[category][key] = message
        else:
            print(f"カテゴリが不明です: {category}")

    def improve_question(self, question):
        system_message = """
        あなたは心理学とインタビュー技法の専門家です。本人が自意識的に取り組んでいないような隠れた認知を取り出すためには、柔軟で自然な会話を通して相手から効果的に情報を引き出すための工夫が必要になります。\n
        インタビューの質問に答えたくなるような、柔軟で受け入れやすい質問文に改善してください。\n
        ただし、以下のインタビュー技法や心理学を用いてください。\n
        1. オープンクエスチョンとクローズドクエスチョンのバランスを取ること。つまり、はいかいいえで答えられる質問のみのターンも設ける。\n
        2. リフレクティブリスニングをすること。例":"その状況は難しそうですが、実際にはどうでしょうか？
        3. 適度にインタビュアーとしての意見や推論を言うこと。例":"過去に何か教訓を得た経験があったから、そうやっているのでしょうか？\n
        4. フレーミング効果を使うこと。例":"この状況でどうしてもうまくいかないと感じることがありますか？\n
        5. 極力最小限の長さにしてください。\n
        """
        prompt = f"次の質問を改善してください。簡単な相槌と、一つの質問のみを生成してください。：\n{question}"

        return self._get_gpt_response(system_message, prompt)

    def check_question(
        self, improved_question, message, messages, elements, attempts=0
    ):
        system_message = """
        あなたはインタビューの専門家で、改善された質問が適切かどうかを判断する役割を持っています。
        初めて聞く内容の質問であれば適切、履歴に類似した内容の質問があれば不適切とし、インタビュー履歴と最新の回答を参考にして、質問が適切かどうかを確認してください。
        類似した内容の基準は、質問の内容がほとんど同じである場合です。
        """

        prompt = f"""
        改善された質問: {improved_question}
        最新の回答: {message}
        インタビュー履歴:
        {messages}

        この質問は適切ですか？適切であればそのまま{improved_question}の質問を出力し、インタビュー履歴{messages}または、直前の回答{message}に類似した内容が既に存在する場合は「不適切」とだけ出力してください。
        """

        checked_response = self._get_gpt_response(system_message, prompt)

        if "不適切" in checked_response:
            attempts += 1

            if attempts >= 3:
                return improved_question

            new_question = self.generate_question(elements, messages, message)
            improved_question = self.improve_question(new_question)

            return self.check_question(
                improved_question, message, messages, elements, attempts
            )

        return improved_question
