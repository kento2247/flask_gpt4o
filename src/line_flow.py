import os
from src.gpt import gpt
from src.line import line
from src.mongodb import mongodb

class line_flow:
    def __init__(self, args):
        self.args=args
        self.config=args.config
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

        # line接続設定
        channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.line_client = line(channel_access_token)

        # gpt接続設定
        gpt_model = self.config["gpt"]["model"]
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gpt_client = gpt(model=gpt_model, api_key=openai_api_key, sleep_api=args.sleep_api)
        
    def update_history(self,messages:list, assistant_message:str, line_id:str):
        content_list = [
            messages[-1],
            {"role": "assistant", "content": assistant_message},
        ]
        self.mongo_db_client.insert_message(line_id, content_list)  # 会話履歴の更新
    
    def follow(self, line_id: str, reply_token: str):
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        messages = [
            {
                "role": "system",
                "content": self.config["initial_message"],
            }
        ]
        response_text = self.gpt_client.get_response(messages)
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
        self.update_history(messages, response_text, line_id)
        return
 
    def exit(self, line_id: str, reply_token: str):
        self.line_client.reply_interview_end(reply_token)
        self.mongo_db_client.initialize_messages(line_id)
        return

    def resume(self, line_id: str, reply_token: str):
        messages = self.mongo_db_client.get_messages(line_id)
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        progress = 7
        reply_message = messages[-1]["content"] # 最後のメッセージを取得
        self.line_client.reply_gpt_response(
            reply_token=reply_token,
            session_id=session_id,
            message=reply_message,
            progress=progress,
            progress_max=self.progress_max,
        )
        return
    
    def message(self, line_id: str, reply_token: str, message: str):
        messages = self.mongo_db_client.get_messages(line_id)  # 会話履歴の取得
        session_id = self.mongo_db_client.sessionid_dict[line_id]
        
        if len(messages) <= 1:  # exitからの再開の場合
            messages = [
                {
                    "role": "system",
                    "content": self.config["initial_message"],
                }
            ]
        else:
            if message =="resume":
                self.resume(line_id, reply_token)
                return
            content_dict = {"role": "user", "content": message}
            messages.append(content_dict)

        response_text = self.gpt_client.get_response(messages)
        progress = 7
        self.line_client.reply_gpt_response(
            reply_token=reply_token,
            session_id=session_id,
            message=response_text,
            progress=progress,
            progress_max=self.progress_max,
        )
        return