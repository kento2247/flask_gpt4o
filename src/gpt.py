import openai


class gpt:
    def __init__(self, model: str, api_key: str, sleep_api: bool = False):
        self.model = model
        openai.api_key = api_key
        self.sleep_api = sleep_api

    def get_response(self, messages: list) -> str:
        try:
            if self.sleep_api:
                response_str = "APIをスリープ中です．"
            else:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                )
                response_str = response.choices[0].message.content
            return response_str
        except Exception as e:
            return f"エラーが発生しました．\n{e}"
