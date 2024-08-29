import openai


class gpt:
    def __init__(self, model: str, api_key: str):
        self.model = model
        openai.api_key = api_key

    def get_response(self, messages: list) -> str:
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            response_str = response.choices[0].message.content
            return f"MK: {response_str}"
        except Exception as e:
            return f"エラーが発生しました．\n{e}"
