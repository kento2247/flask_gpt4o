import uuid


class line_emulater:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.messages = []

    def get_message(self) -> tuple:
        input_message = input("prompt: ")
        return (input_message, self.messages)
    
    def set_initial_question(self, initial_question: str):
        self.messages.append({"role": "assistant", "content": initial_question})
        return

    def update_messages(self, user_message: str, assistant_response: str):
        self.messages.extend(
            [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": assistant_response},
            ]
        )
        return

    def save_messages(self, messages_save_path: str):
        import json

        with open(messages_save_path, "w") as f:
            json.dump(self.messages, f, indent=4, ensure_ascii=False)
        return
