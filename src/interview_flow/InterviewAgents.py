import openai


class InterviewAgents:
    def __init__(self, args):
        self.details = {
            "行動": [],  # 行動に関する回答を蓄積
            "認知": [],  # 認知に関する回答を蓄積
            "情報": [],  # 情報に関する回答を蓄積
        }
        assert args.openai_api_key, "OpenAI APIキーが設定されていません"

        openai.api_key = args.openai_api_key
        self.model = args.config["openai"]["model"]
        self.max_tokens = args.config["openai"]["max_tokens"]
        self.temperature = args.config["openai"]["temperature"]
        self.early_stopping = args.config["openai"]["early_stopping"]
        self.interview_purpose = args.config["interview_purpose"]
        self.question_items = args.config["question_items"]

    def _get_gpt_response(self, sys_message: str, usr_message: str) -> str:
        req_messages = [
            {"role": "system", "content": sys_message},
            {"role": "user", "content": usr_message},
        ]
        response = openai.chat.completions.create(
            model=self.model,
            messages=req_messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def generate_question(self, elements, messages, message):
        system_message = f"""
        あなたはプラントの現場を取材するプロのインタビュアーです．以下の内容に基づいて、従業員に対して現在取り組んでいるタスクとその人の仕事観に関するインタビューを行ってください。
        インタビューは、認知タスク分析を行うためのもので、認知プロセスを理解することと、その根底にある信念を聞き出すことが目的です。
        認知タスク分析とは、熟練者や専門家が、タスクにおいて意識的、あるいは無意識的におこなう意思決定の認知プロセスを探るための手法です。
        インタビューでは、作業者の現在のタスクに関する、認知プロセスにおける**情報**と**認知**と**行動**についてと、第二段階では作業者が仕事に取り組む本音や信念などついての質問をしてください。\n
        直前の回答{message}とそれまでのインタビューの対話{messages}の文脈で、{elements}を埋めるための質問を、{elements}の要素が埋まっていないあるいは情報が少ない項目を優先的に聞くように生成してください。\n
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
        1. 質問は一つのみで、簡潔でわかりやすいものにしてください。{message}を考慮した簡単な相槌も生成してください。\n
        2. 重複した質問を避けてください・\n
        3. 信念、哲学、手がかりという言葉を使わないでさりげなく聞いて下さい。\n
        4. 必ず回答者の**最初の回答で得られた現在のタスクに関する質問**のみを生成してください\n
        5. CDMのプローブはそのまま使わず、文脈に合わせて単語や言い回しを変えてください。\n
        6. 以下の質問技法を使ってください。\n
        
        最後に、以下のインタビュー手順に従ってください。\n
        第一段階：最初の回答で得られた、回答者の現在のタスクに関しての「行動」「認知」「情報」の側面を簡潔に引き出す。行動は日常性や内容、時間的圧力などで、認知は気付きや手がかり、目標などで、情報はもとにした知識や経験についてである。\n
        第二段階：{elements}が埋まってきたら、深堀を行い、どうしてそのように行ったり、考えたり、情報を用いたりするのか、回答者の**信念**や**哲学**などに関わる仕事への姿勢や態度の本音を質問技法を用いて深堀する。\n
        3. {elements}のインタビュー項目がカバーできるまで、インタビューを続ける。\n
        
        質問技法に関して、以下が本音を聞き出すときに有効だと示唆されている以下の技法を文脈に合わせて選択して用いてください。\n
        話を展開する技法：\n
        ダイレクトに尋ねる際：「インタビュアーによる仮説提示」「インタビュアーによる具体物提示」\n
        呼び水とする際「インタビュアーの主観的意見の提示」\n
        雰囲気を作る技法：「共感を示す」、「後押しする」\n
        最後になりますが、一番重要なことは、必ず回答者の**最初の回答で得られた現在のタスクに関する質問**のみを生成することです。\n
        それでは、チャットを開始してください。
        """
        # 分岐処理: elements内の要素に基づいて異なるエージェントを使用する
        # もしすべての要素が2つ以上埋まっている場合、別のエージェントを使用
        #
        if sum(len(v) for v in elements.values()) >= 4:

            # もしすべての要素が2つ以上埋まっている場合、別のエージェントを使用
            prompt = f"""
            インタビュー履歴: {messages}
            最新の回答: {message}

            質問技法を使って、これまでの会話に基づいて回答者の仕事における信念や哲学、本音を引き出す深堀の質問をこれまでの会話内容と絡めて生成してください。
            ただし、信念や哲学は何ですかとダイレクトに聞くのではなく、相手が自然に話しやすいように工夫してください。また、複数の質問をせず、一つの質問のみをなるべく短い一文にまとめて簡潔に生成してください。
            また、まだ深堀ができるような最新の回答であれば、それについて深堀の質問を生成してください。例えば、「高品質なミルクを作る」という最新の回答があれば、それについて「どうしてそれを大切にしているのですか？」などの直前の回答に対して掘り下げた質問を生成してください。具体例は実際に使わないこと。
            制約として、必ず効果的に本音を聞き出すために以下の質問技法を用いてください。\n
            仮説を提示する\n
            具体物を提示する\n
            主観的意見を提示する\n
            共感を示す\n
            後押しをする\n
            また、必ず現在の回答者のタスクに関する質問のみを生成し,インタビュー履歴と似ている質問はしないでください。簡潔に、質問は一個だけ生成してください。
            さらに、「特別」という言葉は使わないことを守ってください。
            """
            return self._get_gpt_response(system_message, prompt)

        else:
            # elementsにまだ埋まっていない項目がある場合、通常の質問生成
            prompt = f"""
            それまでのインタビューの対話{messages}と直前の回答である{message}を参照し、共感か後押しか驚きの提示か理解の提示による相槌と**回答者の現在のタスクに関する一つの質問**を生成してください。「」はいりません。
            {elements}が埋まっていない項目、あるいは、要素が少ない項目から優先的に質問してください。
            背う役として以下を守ってください。
            1. 必ず、最初の回答で得られた回答者の現在のタスクに関しての「行動」「認知」「情報」の側面に焦点を当ててください。
            2. 手がかりという言葉は使わず、なるべく簡潔で分かりやすい質問を生成してください。
            3. 「過去の経験」や「知識」「目標」などは具体的に内容がわかるまで深堀してください。
            4. 認知の側面を聞き出したあとに、それと関連付けて過去の経験や知識などを深堀する流れを意識してください。
            """
            return self._get_gpt_response(system_message, prompt)
        # prompt = f"""
        # それまでのインタビューの対話{messages}と直前の回答である{message}を参照し、共感か後押しによる相槌と**回答者の現在のタスクに関する一つの質問**を生成してください。「」はいりません。
        # {elements}が埋まっていないものあるいは、情報数が少ないものを優先的に質問してください。もしくは、それぞれの深堀を行い、どうしてそのように行ったり、考えたり、情報を用いたりするのか、回答者の信念や哲学などに関わる仕事への姿勢や態度の本音を、質問技法を用いて深堀してください。
        # ただし必ず、最初の回答で得られた回答者の現在のタスクに関しての「行動」「認知」「情報」の側面に焦点を当ててください。
        # """

        # return self._get_gpt_response(system_message, prompt)
    def interview_question(self, messages, message):
        system_message = f"""
        あなたはプラントの現場を取材するプロの半構造化インタビュアーです。以下の内容に基づいて、現場の従業員に対するインタビューを行ってください。\n

        インタビューの目的は、従業員のタスクに対する認知プロセスと、その背景にある従業員の仕事に対する態度や哲学、信念を聞き出すことです。認知プロセスは、認知タスク分析を行うためのものです。認知タスク分析とは、熟練者や専門家が、タスクにおいて意識的、あるいは無意識的におこなう意思決定の認知プロセスを探るための手法です。背景の信念は、そもそもどうして仕事をまじめにやっているのかや、どうして規則を守るのかなどの働く根底となる本音です。\n

        インタビュー手順に関して、半構造化インタビューなので、決まった質問や順番があるわけではなく、インタビューガイドをしっかりと意識する中で自由に質問を考えて構いません。今回の半構造化インタビューにおけるインタビューガイドの項目は、認知タスク分析における行動と認知判断と情報の三つです。インタビューガイドを意識した上で、インタビュー履歴と直前の回答を参照しながら、相手の心に踏み込むことができそうなタイミングで、回答者の深層背景を聞き出してほしいです。\n
        質問を生成するときには、認知タスク分析において用いられる質問プローブであるCDMと、本音を聞き出すときに有効である質問技法を意識、活用してください。以下にこれらの説明を記します。\n
        まず、CDM（Cognitive Dimensions of Notations）は、認知タスク分析の枠組みにおける、過去に発生した非日常的な事象に対して、専門家の判断や意思決定の側面を引き出すための回顧的なインタビュー手法です。しかし、今回は非日常的ではなく日常的な状況で行なわれているタスクを対象としたインタビューに用います。CDMにおけるプローブは、以下のようなものがあります。\n
        手がかり":"何を見て、聞いて、感じていたか？\n
        知識":"この意思決定で使用した情報は何か？その情報はどのようにして得たのか？\n
        類似経験":"過去の経験を思い出したか？\n
        目標":"その時の具体的な目標は何か？\n
        選択肢":"他にどのような行動の選択肢が考えられたか？\n
        根拠":"どのようにしてこの選択肢が選ばれたのか？他の選択肢が拒否された理由は？何か規則があったか？\n
        経験":"この意思決定を行う上で、どのような経験が必要だったか？\n
        支援":"この意思決定が最善ではなかった場合、どのような知識、情報が役立ったか？\n
        時間的圧力":"この意思決定にはどの程度の時間的圧力がかかっていたか？\n
        そして、質問技法に関しては、「話を展開する」ものと「雰囲気を作る」ものに大別したとき、それぞれ以下が本音を聞き出すときに有効だと示唆されている技法です。\n
        話を展開する技法：\n
        ダイレクトに尋ねる際：「仮説提示」「具体物提示」\n
        呼び水とするた際「主観的意見の提示」\n
        雰囲気を作る技法：「共感を示す」、「後押しする」\n

        さて、最後にインタビューにおける制約として、以下を守ってください。\n
        1. 必ず質問は一つのフレーズかつ一個で簡潔な内容にしてください。考えさせられる質問は禁止です。簡単な相槌はうって構いません。\n
        2. 信念、哲学、手がかりという言葉を使わないでさりげなく聞いて下さい。\n
        3. 一回の質問に対して、フォローアップ質問は最大3回です。\n
        4. 質問は、回答者の現在のタスクに関する質問のみを生成してください。\n
        5. 上記の質問技法を使ってください。\n
        6. CDMのプローブはそのまま使わず、文脈に合わせて単語や言い回しを変えてください。\n
        それでは、チャットを開始してください．

        """
        prompt = f"""
        インタビュー履歴: {messages}
        直前の回答: {message}
        現在の作業者のタスクについての認知プロセスと仕事に対する回答者の信念や本音という二つの要素を簡潔に聞き出す一つの質問を生成してください。
        """
        return self._get_gpt_response(system_message, prompt)
    def check_if_interview_should_end(self, messages, elements) -> bool:
        if not self.early_stopping:  # 早期終了が無効の場合は常にFalseを返す
            return False

        # 各側面が2つ以上埋まっているかどうかを確認
        sufficient_elements = sum(len(v) for v in elements.values()) >= 6

        if sufficient_elements:
            # すべての側面が2つ以上埋まっている場合、次はGPTでの確認
            system_message = """
            あなたはインタビューの進行を管理する役割を持っています。
            インタビューでは作業者の現在のタスクについての認知タスク分析のためのインタビューを行い、
            頻度や内容、時間的圧力などの行動、気付きや目標、手がかりなどの認知、
            知識や経験などの情報を引き出そうとしています。

            メッセージ履歴と抽出された各側面の情報に基づき、インタビューで現在のタスクに関する
            「行動」「認知」「情報」の各側面が具体的にそれぞれ引き出されているかを判断し、
            すべて引き出している場合にインタビューを終了してください。
            インタビューを終了すべきであれば「終了」とだけ返してください。
            """

            prompt = f"""
            メッセージ履歴:
            {messages}
            引き出された「行動」「認知」「情報」の各側面：
            {elements}

            インタビューは終了すべきですか？現在のタスクに関する「行動」「認知」「情報」の各側面を具体的に
            引き出しているか、メッセージ履歴と引き出された各側面をもとに判断してください。
            """

            # GPTに最終確認を依頼し、終了かどうかを判断
            return "終了" in self._get_gpt_response(system_message, prompt)

        # もし各要素が十分に埋まっていなければ終了しない
        return False

    def extract_elements(self, message, messages, elements):
        system_message = """
        あなたは認知タスク分析の専門家です。
        最新の回答が「行動」「認知」「情報」のどのカテゴリに該当するかを判断し、そのカテゴリ名を明示的に返答してください。
        行動は日常性や行動の内容、時間的圧力などの情報が含まれ、認知は気付きや手がかり、選択肢や目標などの情報が含まれ、情報は、行動において用いる知識や経験などの参考にしていることが含まれます。また、その人の本音や信念に関しての回答は、行動、認知、情報のどれに関係するかを考慮して分類してください。
        例えば、回答が行動に関連する場合、「行動」とだけ出力してください。
        """

        prompt = f"""
        最新の回答: {message}
        メッセージ履歴:
        {messages}

        最新の回答がどのカテゴリ（行動、認知、情報）に該当するかを明確に示してください。行動は日常性や内容、時間的圧力などの情報が含まれ、認知は気付きや手がかり、選択肢や目標などの情報が含まれ、情報は、行動において用いる知識や経験などの参考にしていることが含まれます。態度は、仕事に対する態度や哲学、信念などが含まれます。カテゴリ名のみを出力してください。
        """

        updated_category = self._get_gpt_response(system_message, prompt).strip()

        print("dbから持ってきたelements", elements)
        print("抽出したカテゴリ", updated_category)
        print("最新の回答", message)

        elements = self._add_to_details(updated_category, message, elements)

        print("更新後のelements", elements)
        return elements

    def manage_interview_guide(self, messages, message, interview_purpose, question_items,interview_guide=None):
        """
        インタビューガイドを管理し、目的と質問項目に基づいて回答の要約を生成する。

        :param messages: インタビューのメッセージ履歴
        :param message: 最新のメッセージ
        :param interview_purpose: インタビューの目的
        :param question_items: 質問項目のリスト
        :return: 更新されたインタビューガイド
        """
        # インタビューガイドが提供されていない場合は初期化
        # 初回のみinterview_guideを初期化
        if interview_guide is None:
            interview_guide = {
                "interview_purpose": interview_purpose,
                "interviewguide": {}
            }

        # 各質問項目に対する回答の要約を生成
        for question in question_items:
            system_message = """
            あなたはインタビューガイドを管理するエージェントです。
            最新のメッセージの内容を簡潔に要約し、
            インタビューガイドの該当項目を一か所のみ更新してください。
            """

            prompt = f"""
            インタビューの目的: {interview_purpose}
            質問: {question}
            メッセージ履歴: {messages}
            最新のメッセージ: {message}

            上記の情報をもとに、該当する一つ「{question}」に関する回答の要約のみを簡潔に出力してください。
            """

            # GPTを使用して要約を生成
            summary = self._get_gpt_response(system_message, prompt)
            if summary:
                interview_guide["interviewguide"][question] = summary.strip()

        return interview_guide

    def gpt_generate_question(self, messages, message, interview_guide, judge_end, advice):
        system_message = """
        役割：あなたは、半構造化インタビューを行うインタビュアーです。インタビューの流れと制約に従い、相槌を含めて半構造化インタビューの会話を行ってください。\n
        目的：インタビューガイドに従い、対話履歴と直前の回答を参照しながら、半構造化インタビューを行ってください。インタビューは短くて構いませんが、深堀して思いの真相を聞き出すことを意識してください。インタビューガイドは上から優先度が高い順に質問項目が並んでいます。\n
        内容説明：
        半構造化インタビューは、あらかじめ用意されたインタビューガイドに基づいて進行しますが、回答者の発言に応じて質問を追加したり、変更したりすることが可能なインタビュー手法です。半構造化インタビューでは、対象者が自由に意見を述べられるようにしつつ、研究のテーマや目標に焦点を当てる必要があります。
        インタビューガイドは、調査の目標に基づいて設計され、インタビューの方向性を明確にするもので、インタビューの目的と大まかな質問項目が示されています。インタビューガイドの項目の情報が増えてきたらインタビューは終了です。\n
        インタビューの流れ：
        1.初めに緊張を和らげるための序盤の質問をする
        2.インタビューの趣旨を簡単に説明し、そのあと、本題のインタビューに入る
        3.インタビューに参加してくれたことに対する感謝を示して終了する
        質問については、以下のことを守ってください。\n
        1.具体的かつ簡潔で明確な質問
        2.誘導的でない質問
        3.オープンエンドな質問
        4. 本音や、背景にある意味や動機を引き出すために、仮説の提示,具体物を提示,主観的意見の提示,共感,後押しの技法を使う\n
        5. 相槌と質問は一つのみで,短いフレーズで構成する。例えば、内容と手順と頻度を一度に聞くのではなく、それぞれに分けて質問する\n
        また、以下の制約を守って下ください。\n
        1. 感情予測に基づく終了判定がyesの時は、質問内容を変えるか、インタビューを終了する
        2. インタビューの進行の評価とアドバイスを参考にして、インタビューを行う
        """
        prompt = f"""
        インタビューガイド: {interview_guide}
        インタビュー進行の評価とアドバイス: {advice}
        メッセージ履歴: {messages}
        直前の回答: {message}
        感情に基づく終了判定: {judge_end}
        半構造化インタビューのプロとして、簡潔な一つの質問を生成し必ずインタビューガイドとアドバイスに沿いながら、フォローアップ質問をしつつインタビューしてください。何個も同時に聞かれると、相手は嫌に感じます。
        感情に基づく終了判定がyesの場合、インタビューを終了してください。
        インタビューは短くて構いません。
        """
        question = self._get_gpt_response(system_message, prompt)
        return question

    def check_question(
        self, question, message, messages, attempts=0, interview_guide=None, judge_end=None
    ):
        system_message = """
        あなたはインタビューの専門家で、改善された質問が適切かどうかを判断する役割を持っています。
        初めて聞く内容の質問であれば適切、履歴に類似した内容の質問があれば不適切とし、インタビュー履歴と最新の回答を参考にして、質問が新しい内容で、似た質問をそれまでに生成していないか、予想される回答がインタビュー履歴にないかどうか判断し、質問として適切かどうかを確認してください。
        類似した内容の基準は、質問の意図が似ている場合です。
        """

        prompt = f"""
        改善された質問: {question}
        最新の回答: {message}
        インタビュー履歴:
        {messages}

        この質問は適切ですか？過去に類似した質問がなく適切であれば、{question}をそのまま出力し、インタビュー履歴{messages}または、直前の回答{message}に類似した内容が既に存在する場合は「不適切」とだけ出力してください。
        """

        # checked_response = self._get_gpt_response(system_message, prompt)

        # if "不適切" in checked_response:
        #     attempts += 1

        #     if attempts >= 5:
        #         return improved_question

        #     new_question = self.generate_question(elements, messages, message)
        #     improved_question = self.improve_question(new_question)

        #     return self.check_question(
        #         improved_question, message, messages, elements, attempts
        #     )

        # return improved_question

        checked_response = self._get_gpt_response(system_message, prompt)

        if "不適切" in checked_response:
            attempts += 1

            if attempts >= 7:
                return question

            # 新しい質問を生成

            new_question = self.gpt_generate_question(messages, message, interview_guide, judge_end)

            # 再度、生成した質問の適切性を確認
            return self.check_question(new_question, message, messages, attempts, interview_guide, judge_end)

        return checked_response

    def evaluate_interview_direction(self, messages, message, interview_purpose, question_items):
        system_message = """
        あなたはインタビューの方向性を評価する専門家です。
        インタビューガイドから大きくそれていないか、フォローアップ質問が続きすぎて本題とずれていないかを評価し、その思考過程をアドバイスとして出力してください。
        """

        prompt = f"""
        インタビュー履歴: {messages}
        直前の回答: {message}
        インタビューガイド: {interview_purpose}, {question_items}

        この質問がインタビューガイドに沿っているか、またフォローアップ質問が続きすぎて本題とずれていないかを評価し、アドバイスを出力してください。
        問題がある場合は、どのように修正すべきかのアドバイスも含めてください。
        """

        advice = self._get_gpt_response(system_message, prompt)
        return advice

    def judge_end(self,messages,message):
        system_message = """
        あなたは、回答者がインタビュー中に不快や退屈を感じているかを判断するエージェントです。対話履歴{messages}と{message}を参照して、「つまらない」、「もういい」、「疲れた」などの表現や、「うん」「はい」などの単調な返答があるなどを手掛かりに、相手がインタビューに対して不快に感じているかを判断し、インタビューを終了した方がよいほど不快に感じていると判断した場合はyes、そうでない場合はnoを返してください。
        """
        prompt = f"""
        対話履歴: {messages}
        最新の回答: {message}
        話題を変えたり、インタビューを終了するべきか、回答者の感情を予測しyesかnoで回答してください。
        """
        judge_end=self._get_gpt_response(system_message, prompt)
        return judge_end

    # def _add_to_details(self, category, message, elements) -> dict:
    #     required_keys = self.details.keys()

    #     for key in required_keys:
    #         if key not in elements:
    #             elements[key] = []

    #     if category in elements:
    #         elements[category].append(message)
    #     else:
    #         print(f"カテゴリが不明です: {category}")

    #     return elements

    # def improve_question(self, question):
    #     system_message = """
    #     あなたは心理学とインタビュー技法の専門家です。本人が自意識的に取り組んでいないような隠れた認知を取り出すためには、柔軟で自然な会話を通して相手から効果的に情報を引き出すための工夫が必要になります。\n
    #     インタビューの質問に答えたくなるような、柔軟で受け入れやすい質問文に改善してください。\n
    #     ただし、以下のインタビュー技法や心理学を用いてください。\n
    #     1. オープンクエスチョンとクローズドクエスチョンのバランスを取ること。\n
    #     2. リフレクティブリスニングをすること。例":"その状況は難しそうですが、実際にはどうでしょうか？
    #     3. 適度にインタビュアーとしての意見や推論を言うこと。例":"過去に何か教訓を得た経験があったから、そうやっているのでしょうか？\n
    #     4. フレーミング効果を使うこと。例":"この状況でどうしてもうまくいかないと感じることがありますか？\n
    #     5. 極力最小限の長さにすること。\n
    #     """
    #     prompt = f"次の質問を改善してください。相槌と、一つの質問のみを生成してください。なるべく短い文でまとめてください。ただし、それは興味深いですねとそれは面白いですねはやめてください。：\n{question}"

    #     return self._get_gpt_response(system_message, prompt)

    # def check_question(
    #     self, improved_question, message, messages, elements, attempts=0
    # ):
    #     system_message = """
    #     あなたはインタビューの専門家で、改善された質問が適切かどうかを判断する役割を持っています。
    #     初めて聞く内容の質問であれば適切、履歴に類似した内容の質問があれば不適切とし、インタビュー履歴と最新の回答を参考にして、質問が新しい内容で、似た質問をそれまでに生成していないか、予想される回答がインタビュー履歴にないかどうか判断し、質問として適切かどうかを確認してください。
    #     類似した内容の基準は、質問の意図が似ている場合です。
    #     例えば、注意、手がかり、情報、経験などの単語が出現するのが二回目であれば、不適切としてください。
    #     """

    #     prompt = f"""
    #     改善された質問: {improved_question}
    #     最新の回答: {message}
    #     インタビュー履歴:
    #     {messages}

    #     この質問は適切ですか？過去に類似した質問がなく、適切であればそのまま{improved_question}の質問を出力し、インタビュー履歴{messages}または、直前の回答{message}に類似した内容が既に存在する場合は「不適切」とだけ出力してください。
    #     """

    #     # checked_response = self._get_gpt_response(system_message, prompt)

    #     # if "不適切" in checked_response:
    #     #     attempts += 1

    #     #     if attempts >= 5:
    #     #         return improved_question

    #     #     new_question = self.generate_question(elements, messages, message)
    #     #     improved_question = self.improve_question(new_question)

    #     #     return self.check_question(
    #     #         improved_question, message, messages, elements, attempts
    #     #     )

    #     # return improved_question

    #     checked_response = self._get_gpt_response(system_message, prompt)

    #     if "不適切" in checked_response:
    #         attempts += 1

    #         if attempts >= 7:
    #             return improved_question

    #         # 新しい質問を生成
    #         new_question = self.generate_question(elements, messages, message)

    #         # 再度、生成した質問の適切性を確認
    #         return self.check_question(
    #             new_question, message, messages, elements, attempts
    #         )

    #     return improved_question

    # def generate_summary(self, messages):
    #     system_message = """
    #     あなたはインタビューの専門家です。これまでのメッセージ履歴をもとに、インタビューの総括を行ってください。
    #     インタビューの内容を簡潔にまとめ、インタビューがどのような流れで進んだか、主なポイントを明確にしてください。最後に、インタビューの終わりとして相手に感謝の言葉を伝える一文を加えてください。
    #     """

    #     # メッセージ履歴を踏まえた総括を生成
    #     prompt = f"""
    #     メッセージ履歴: {messages}

    #     このメッセージ履歴に基づいて、インタビューの総括を行ってください。
    #     """
    #     summary_response = self._get_gpt_response(system_message, prompt)
    #     return summary_response
