import os

# from src.gpt import gpt
from src.line import line
from src.mongodb import mongodb
from src.interview_flow.InterviewAgents import InterviewAgents


class message_flow:
    def __init__(self, args):
        self.args = args
        self.config = args.config
        self.progress_max = self.config["flow"]["progress_max"]
        # mongodb接続設定
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_app_name = self.config["mongodb"]["app_name"]
        mongodb_db_name = self.config["mongodb"]["db_name"]
        self.mongo_db_client = mongodb(
            username=mongodb_username,
            password=mongodb_password,
            app_name=mongodb_app_name,
            db_name=mongodb_db_name,
        )
        self.interview_agents = InterviewAgents(args)

        # line接続設定
        channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.line_client = line(channel_access_token)

        # gpt接続設定
        gpt_model = self.config["openai"]["model"]
        openai_api_key = os.getenv("OPENAI_API_KEY")
        # self.gpt_client = gpt(
        #     model=gpt_model, api_key=openai_api_key, sleep_api=args.sleep_api
        # )

    def message_parser(self, request_json):
        parse_data = self.line_client.parse_webhook(request_json)

        self.event_type = parse_data["event_type"]
        self.line_id = parse_data["line_id"]
        self.reply_token = parse_data["reply_token"]
        self.message = parse_data["message"]

        if self.event_type == "follow":
            self._follow()
        elif self.event_type == "message":
            if self.message == "exit":
                self._exit()
            else:
                self._message()  # messageの中でresumeがあるか判定

    def error_send(self, error_message: str):
        self.line_client.reply(self.reply_token, error_message)
        return

    def _update_history(self, message_dict: dict, assistant_message: str):
        content_list = [  # 二つのメッセージを同時に保存(user or system, assistant)
            message_dict,
            {"role": "assistant", "content": assistant_message},
        ]
        self.mongo_db_client.insert_message(
            self.line_id, content_list
        )  # 会話履歴の更新
        return

    def _follow(self):
        session_id = self.mongo_db_client.sessionid_dict[self.line_id]
        response_text = self._generate_question(
            session_id,
            "",
            [],
        )
        self.line_client.reply_gpt_response(
            reply_token=self.reply_token,
            session_id=session_id,
            message=response_text,
            progress=0,
            progress_max=self.progress_max,
        )  # lineでの返信
        self.mongo_db_client.initialize_messages(
            self.line_id
        )  # 既存のセッションがあれば終了させ，新しいセッションを作成
        self._update_history([], response_text)
        return

    def _exit(self):
        self.line_client.reply_interview_end(self.reply_token)
        self.mongo_db_client.initialize_messages(self.line_id)
        return

    def _resume(self):
        messages = self.mongo_db_client.get_messages(self.line_id)
        session_id = self.mongo_db_client.sessionid_dict[self.line_id]
        progress = 7
        reply_message = messages[-1]["content"]  # 最後のメッセージを取得
        self.line_client.reply_gpt_response(
            reply_token=self.reply_token,
            session_id=session_id,
            message=reply_message,
            progress=progress,
            progress_max=self.progress_max,
        )
        return

    def _message(self):
        messages = self.mongo_db_client.get_messages(self.line_id)  # 会話履歴の取得
        session_id = self.mongo_db_client.sessionid_dict[self.line_id]

        if self.message == "resume" and len(messages) > 1:
            self._resume()
            return

        messages.append({"role": "user", "content": self.message})

        response_text, progress = self._generate_question(
            self.message, messages, self.message
        )
        self.line_client.reply_gpt_response(
            reply_token=self.reply_token,
            session_id=session_id,
            message=response_text,
            progress=progress,
            progress_max=self.progress_max,
        )

        self._update_history(messages[-1], response_text)
        return

    def _generate_question(self, session_id, message, messages):
        # TODO ここに，チャピの回答を取得する処理を書く

        if len(messages) <= 1:
            assistant_response = "本日はあなたの意思決定を伴う作業やお仕事について、お尋ねしたいです。貴重なお時間をいただき、ありがとうございます！早速ですが、最近の日常的なタスクを教えていただけますか？"  # TODO ちゃぴに作らせる
            progress = 0

        else:
            # 通常の質問生成と進捗管理の処理
            elements = self.interview_agents.extract_elements(
                message, messages
            )  # インタビュー状況を把握
            print(elements)
            print(messages)
            # インタビューを終了すべきかチェック
            if self.interview_agents.check_if_interview_should_end(messages, elements):
                assistant_response = (
                    "本日はインタビューのお時間をいただきありがとうございました"
                )
                progress = 5  # インタビュー終了時の進捗
            else:
                question = self.interview_agents.generate_question(
                    message, elements, messages
                )  # 質問を生成
                improved_question = self.interview_agents.improve_question(
                    question
                )  # 質問を改善
                checked_question = self.interview_agents.check_question(
                    improved_question, message, messages, elements, attempts=0
                )  # 質問が適切かどうかをチェック. attemptsの初期値は0
                assistant_response = checked_question
                progress = 5  # インタビュー進捗

        return assistant_response, progress
