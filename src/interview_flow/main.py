def generate_question(self, session_id, message, messages):
    interview_purpose = self.config["interview_purpose"]
    question_items = self.config["question_items"]
    if len(messages) <= 0:
        assistant_response = "本日はよろしくお願いします！"
        # progress = 0
    else:
        judge_end = interview_agents.judge_end(messages, message)
        interview_guide = interview_agents.manage_interview_guide(messages, message, interview_purpose, question_items, interview_guide=None)
        question = interview_agents.gpt_generate_question(messages, message, interview_guide, judge_end)
        improved_question= interview_agents.check_question(question, message, messages, attempts=0)
        assistant_response = improved_question
    return assistant_response, progress
    
    # TODO ここに，チャピの回答を取得する処理を書く

    # if len(messages) <= 0:
    #     assistant_response = "現在、どんな作業をしていますか？"  # TODO ちゃぴに作らせる
    #     progress = 0

    # else:
    #     # 通常の質問生成と進捗管理の処理
    #     elements = interview_agents.extract_elements(
    #         message, messages
    #     )  # インタビュー状況を把握
    #     # print(elements)
    #     # print(messages)
    #     # インタビューを終了すべきかチェック
    #     if interview_agents.check_if_interview_should_end(messages, elements):
    #         assistant_response = (
    #             "本日はインタビューのお時間をいただきありがとうございました"
    #         )
    #         progress = 5  # インタビュー終了時の進捗
    #     else:
    #         question = interview_agents.generate_question(
    #             message, elements, messages
    #         )  # 質問を生成
    #         improved_question = interview_agents.improve_question(
    #             question
    #         )  # 質問を改善
    #         checked_question = interview_agents.check_question(
    #             improved_question, message, messages, elements, attempts=0
    #         )  # 質問が適切かどうかをチェック. attemptsの初期値は0
    #         assistant_response = checked_question
    #         progress = 5  # インタビュー進捗

    # return assistant_response, progress


"""ここより下は一切変更不要。LINE botと同じような入出力にするためのコード"""
import argparse
import os

from dotenv import load_dotenv

load_dotenv()
args = argparse.Namespace()
args.openai_api_key = os.environ["OPENAI_API_KEY"]
args.config = {
    "openai": {
        "model": "gpt-4o",
        "max_tokens": 100,
        "temperature": 0.5,
        "early_stopping": True,
    }
}


messages_save_path = "/home/mana/tmp/messages.json"

from InterviewAgents import InterviewAgents

interview_agents = InterviewAgents(args)


def main():
    from src.line_emulater import line_emulater

    line_emulater = line_emulater()
    session_id = line_emulater.session_id

    initial_question, progress = generate_question(session_id, "", [])
    print(f"assistante: {initial_question}", progress)
    line_emulater.set_initial_question(initial_question)

    while True:
        message, messages = line_emulater.get_message()  # ユーザーの入力を受け取る

        if message == "exit":  # ユーザーがexitと入力したら終了
            break

        assistant_response, progress = generate_question(session_id, message, messages)
        print(f"assistante: {assistant_response}", progress)

        line_emulater.update_messages(message, assistant_response)

    # messages_saev_pathにmessagesを保存する
    line_emulater.save_messages(messages_save_path)


if __name__ == "__main__":
    main()
