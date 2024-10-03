def generate_question(session_id, message, messages):
    # TODO ここに，チャピの回答を取得する処理を書く

    if message == "" and len(messages) == 0:
        assistant_response = "本日はあなたの意思決定を伴う作業やお仕事について、お尋ねしたいです。貴重なお時間をいただき、ありがとうございます！早速ですが、最近の日常的なタスクを教えていただけますか？"  # TODO ちゃぴに作らせる
        progress = 0

    else:
        # 通常の質問生成と進捗管理の処理
        elements = interview_agents.extract_elements(
            message, messages
        )  # インタビュー状況を把握
        print(elements)
        print(messages)
        # インタビューを終了すべきかチェック
        if interview_agents.check_if_interview_should_end(messages, elements):
            assistant_response = (
                "本日はインタビューのお時間をいただきありがとうございました"
            )
            progress = 5  # インタビュー終了時の進捗
        else:
            question = interview_agents.generate_question(
                message, elements, messages
            )  # 質問を生成
            improved_question = interview_agents.improve_question(
                question
            )  # 質問を改善
            checked_question = interview_agents.check_question(
                improved_question, message, messages, elements, attempts=0
            )  # 質問が適切かどうかをチェック. attemptsの初期値は0
            assistant_response = checked_question
            progress = 5  # インタビュー進捗

    return assistant_response, progress


"""ここより下は一切変更不要。LINE botと同じような入出力にするためのコード"""
import argparse
import os

from dotenv import load_dotenv

load_dotenv()
args = argparse.Namespace()
args.openai_api_key = os.environ["OPENAI_API_KEY"]
args.config = {
    "model": "gpt-4o",
    "max_tokens": 100,
    "temperature": 0.5,
    "early_stopping": False,
}


messages_save_path = "/home/mana/flask_gpt4o/tmp/messages.json"

from interview_flow.InterviewAgents import InterviewAgents

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
