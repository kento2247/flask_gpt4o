from src.line_emulater import line_emulater


def get_assistant_response(session_id, message, messages):
    # TODO ここに，チャピの回答を取得する処理を書く

    assistant_response = "test"
    progress = 0

    return assistant_response, progress


def main():
    while True:
        session_id, message, messages = (
            line_emulater.get_message()
        )  # ユーザーの入力を受け取る

        assistant_response, progress = get_assistant_response(
            session_id, message, messages
        )

        line_emulater.update_messages(message, assistant_response)

        print(line_emulater.messages, progress)


if __name__ == "__main__":
    line_emulater = line_emulater()
    main()
