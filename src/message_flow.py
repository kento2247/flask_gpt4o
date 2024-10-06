import os

from src.interview_flow.InterviewAgents import InterviewAgents

# from src.gpt import gpt
from src.line import line
from src.mongodb import mongodb


class message_flow:
    def __init__(self, args):
        self.args = args
        self.config = args.config
        self.progress_max = self.config["flow"]["progress_max"]

        # mongodb接続設定
        mongodb_username = os.getenv("MONGODB_USERNAME")
        mongodb_password = os.getenv("MONGODB_PASSWORD")
        mongodb_database_name = self.config["mongodb"]["database_name"]
        mongodb_collection_name = self.config["mongodb"]["collection_name"]
        self.mongo_db_client = mongodb(
            username=mongodb_username,
            password=mongodb_password,
            database_name=mongodb_database_name,
            collection_name=mongodb_collection_name,
        )
        self.interview_agents = InterviewAgents(args)

        # line接続設定
        channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.line_client = line(channel_access_token)

        # # gpt接続設定
        # gpt_model = self.config["openai"]["model"]
        # openai_api_key = os.getenv("OPENAI_API_KEY")
        # # self.gpt_client = gpt(
        # #     model=gpt_model, api_key=openai_api_key, sleep_api=args.sleep_api
        # # )

        # 処理中のline_idの保持. {line_id: {reply_token: reply_token, message: message}}
        self.processing_dict = {}

    def message_parser(self, request_json):
        parse_data = self.line_client.parse_webhook(request_json)

        event_type = parse_data["event_type"]
        line_id = parse_data["line_id"]
        reply_token = parse_data["reply_token"]
        message = parse_data["message"]

        if line_id in self.processing_dict:
            print("line_id is already in processing_dict")
            return None

        else:
            self.processing_dict[line_id] = {
                "reply_token": reply_token,
                "message": message,
            }

            if event_type == "follow":
                self._follow(line_id)
            elif event_type == "message":
                if message == "exit":
                    self._exit(line_id)
                else:
                    self._message(line_id)  # messageの中でresumeがあるか判定

            del self.processing_dict[line_id]
            return

    def error_send(self, error_message: str):
        # self.line_client.reply(self.reply_token, error_message)
        developper_line_id = self.config["line"]["developper_line_id"]
        self.line_client.push_message(developper_line_id, error_message)
        return

    def _update_history(self, line_id: str, message: str, assistant_message: str):
        if message and message != "resume":
            content_list = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_message},
            ]
        else:
            content_list = [{"role": "assistant", "content": assistant_message}]
        self.mongo_db_client.insert_message(line_id, content_list)  # 会話履歴の更新
        return

    def _follow(self, line_id: str):
        print("follow")
        reply_token = self.processing_dict[line_id]["reply_token"]
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        response_text = self._generate_question(
            session_id,
            "",
            [],
        )
        self.line_client.reply_gpt_response(
            reply_token=reply_token,
            session_id=session_id,
            message=response_text,
            progress=0,
            progress_max=self.progress_max,
        )  # lineでの返信
        self.mongo_db_client.initialize_messages(
            line_id
        )  # 既存のセッションがあれば終了させ，新しいセッションを作成
        self._update_history(line_id, [], response_text)
        return

    def _exit(self, line_id: str):
        print("exit")
        reply_token = self.processing_dict[line_id]["reply_token"]
        self.line_client.reply_interview_end(reply_token)
        self.mongo_db_client.initialize_messages(line_id)
        return

    def _resume(self, line_id: str):
        print("resume")
        messages = self.mongo_db_client.get_messages(line_id)
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        reply_token = self.processing_dict[line_id]["reply_token"]

        progress = 7
        reply_message = messages[-1]["content"]  # 最後のメッセージを取得
        self.line_client.reply_gpt_response(
            reply_token=reply_token,
            session_id=session_id,
            message=reply_message,
            progress=progress,
            progress_max=self.progress_max,
        )
        return

    def _message(self, line_id: str):
        messages = self.mongo_db_client.get_messages(line_id)  # 会話履歴の取得
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        message = self.processing_dict[line_id]["message"]
        reply_token = self.processing_dict[line_id]["reply_token"]

        if message == "resume" and len(messages) > 1:
            self._resume(line_id)
            return

        response_text, progress = self._generate_question(session_id, message, messages)
        self.line_client.reply_gpt_response(
            reply_token=reply_token,
            session_id=session_id,
            message=response_text,
            progress=progress,
            progress_max=self.progress_max,
        )

        self._update_history(line_id, message, response_text)
        return

    def _generate_question(self, session_id, message, messages):
        # TODO ここに，チャピの回答を取得する処理を書く

        if len(messages) <= 0:
            assistant_response = (
                "現在、どんな作業をしていますか？"  # TODO ちゃぴに作らせる
            )
            progress = 0

        else:
            # 通常の質問生成と進捗管理の処理
            elements = self.interview_agents.extract_elements(
                message, messages
            )  # インタビュー状況を把握
            # print(elements)
            # print(messages)
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
