import openai
from dotenv import load_dotenv
import os

load_dotenv()
# OpenAI APIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")


# # 質問生成エージェント
# def generate_interview_questions(
#     context="現場における日常的な作業やタスクにおける意思決定",
# ):
#     messages = [
#         {"role": "system", "content": "あなたはインタビュアーです。"},
#         {
#             "role": "user",
#             "content": f"現場における日常的な作業やタスクにおける意思決定に関して、行動、情報、認知の側面を明らかにする質問を生成してください。",
#         },
#     ]

#     response = openai.ChatCompletion.create(
#         model="gpt-4", messages=messages, max_tokens=150  # GPT-4モデルを指定
#     )

#     questions = response["choices"][0]["message"]["content"].strip()
#     return questions


# # 使用例
# context = "現場における日常的な作業やタスクにおける意思決定"
# questions = generate_interview_questions(context)
# print(questions)


# # 回答分析エージェント
# def analyze_response(response_text, state):
#     messages = [
#         {
#             "role": "system",
#             "content": "あなたはインタビューの回答を分析するエージェントです。",
#         },
#         {
#             "role": "user",
#             "content": f"インタビュイーの回答: {response_text}。回答が具体的に行動、情報、認知をカバーしているかを判定してください。",
#         },
#     ]

#     response = openai.ChatCompletion.create(
#         model="gpt-4", messages=messages, max_tokens=200  # GPT-4モデルを指定
#     )

#     analysis = response["choices"][0]["message"]["content"].strip()

#     # 分析結果に基づいてフラグを更新
#     if "行動" in analysis and "十分に具体的" in analysis:
#         state["action_covered"] = True
#     if "情報" in analysis and "十分に具体的" in analysis:
#         state["information_covered"] = True
#     if "認知" in analysis and "十分に具体的" in analysis:
#         state["cognition_covered"] = True
#     return analysis, state


# # 各側面がカバーされたかどうかを確認する関数
# def check_completion(state):
#     # state内の全てのフラグがTrueであればインタビューを完了
#     return all(state.values())


# def manage_interview_flow(questions, response_text, state):
#     if check_completion(state):
#         return "インタビューが完了しました。ありがとうございました。", state

#     messages = [
#         {
#             "role": "system",
#             "content": "あなたはインタビューフローを管理するエージェントです。",
#         },
#         {
#             "role": "user",
#             "content": f"質問: {questions} \n回答: {response_text} \n次に尋ねるべき質問を生成してください。",
#         },
#     ]

#     response = openai.ChatCompletion.create(
#         model="gpt-4", messages=messages, max_tokens=150  # GPT-4モデルを指定
#     )

#     next_question = response["choices"][0]["message"]["content"].strip()
#     return next_question, state


# def run_interview():
#     # コンテキストを「現場における日常的な作業やタスクにおける意思決定」に設定
#     context = "現場における日常的な作業やタスクにおける意思決定"

#     # 質問生成エージェントによる最初の質問の生成
#     questions = generate_interview_questions(context)
#     print(f"最初の質問: {questions}")

#     # 各側面のカバー状態を管理するフラグ
#     state = {
#         "action_covered": False,
#         "information_covered": False,
#         "cognition_covered": False,
#     }

#     while True:
#         # インタビュイーの回答を入力（ここでは手動入力の例）
#         response_text = input("\nインタビュイーの回答: ")

#         # '終了'が入力された場合、インタビューを強制終了
#         if response_text.lower() == "終了":
#             print("インタビューを終了します。")
#             break

#         # 回答を分析し、各フラグを更新
#         analysis, state = analyze_response(response_text, state)
#         print(f"\n回答の分析結果: {analysis}")

#         # すべての要素がカバーされているか確認し、インタビューを終了するか次の質問を生成
#         if check_completion(state):
#             print("\nインタビューが完了しました。ありがとうございました。")
#             break

#         # 次の質問を決定
#         next_question, state = manage_interview_flow(questions, response_text, state)
#         print(f"\n次の質問: {next_question}")

#         # 次の質問を次のループで使用するために更新
#         questions = next_question


# インタビューの状態を記録（全ての項目がTrueの場合にTrueを返す）
def check_completion(state):
    return all(
        state["covered"].values()
    )  # 全ての要素がTrueになった場合にインタビューを終了


# 短い回答や不機嫌な反応を判定する関数
def check_short_or_unhappy_response(response_text):
    short_responses = ["ない", "特にない", "わからない", "知らない", "特になし", "終了"]
    return len(response_text.split()) <= 2 or response_text.lower() in short_responses


# 質問生成エージェント（最初の作業に基づき、脱線しない質問を生成）
def generate_interview_questions(response_text, state, first_task):
    # 不機嫌や短い返答をチェック
    if check_short_or_unhappy_response(response_text):
        return "インタビューを終了します。ありがとうございました。"

    # カバーされていない項目に応じた質問を生成（最初の作業に関連する質問のみ）
    if not state["covered"]["action"] and state["count"]["action"] < 2:
        state["count"]["action"] += 1  # カウントを増やす
        prompt = f"インタビュイーの回答: {response_text}。最初の作業「{first_task}」に関連する行動や頻度、緊急性について質問を生成してください。ただし、質問は短く脱線しないようにし、インタビュー技法やプロービングを活用すること。"
    elif not state["covered"]["cognition"] and state["count"]["cognition"] < 2:
        state["count"]["cognition"] += 1  # カウントを増やす
        prompt = f"インタビュイーの回答: {response_text}。最初の作業「{first_task}」に関して、その作業の意図や判断に関する質問を生成してください。ただし、質問は短く脱線しないようにし、インタビュー技法やプロービングを活用すること。"
    elif not state["covered"]["information"] and state["count"]["information"] < 2:
        state["count"]["information"] += 1  # カウントを増やす
        prompt = f"インタビュイーの回答: {response_text}。最初の作業「{first_task}」に関して、作業に用いている情報や知識、経験について質問を生成してください。ただし、質問は短く脱線しないようにし、インタビュー技法やプロービングを活用すること。"
    else:
        return "インタビューが完了しました。ありがとうございました。"

    # OpenAI API で次の質問を生成
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "あなたはインタビュアーです。インタビュイーの回答に基づき、具体的かつ自然な質問を1つ生成してください。",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
    )

    next_question = response["choices"][0]["message"]["content"].strip()
    return next_question


# 回答分析エージェント（行動、情報、認知をカバーしているかを判定）
def analyze_response(response_text, state):
    messages = [
        {
            "role": "system",
            "content": "あなたはインタビューの回答を分析するエージェントです。",
        },
        {
            "role": "user",
            "content": (
                f"インタビュイーの回答: {response_text}。\n"
                "次の3つの項目について、カバーされているかYes/Noで答えてください：\n"
                "1. 行動（具体的な手順、頻度、緊急性について情報が含まれているか）。\n"
                "2. 認知（目的、判断、予測、代替案について情報が含まれているか）。\n"
                "3. 情報（知識、経験、使用している情報源について情報が含まれているか）。"
            ),
        },
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=messages, max_tokens=300  # 必要に応じて調整可能
    )

    analysis = response["choices"][0]["message"]["content"].strip()

    # 分析結果をもとに、フラグを更新
    if "行動: Yes" in analysis:
        state["covered"]["action"] = True
    if "認知: Yes" in analysis:
        state["covered"]["cognition"] = True
    if "情報: Yes" in analysis:
        state["covered"]["information"] = True

    return analysis, state


# インタビューフロー管理エージェント
def manage_interview_flow(response_text, state, first_task):
    if check_completion(state):
        return "インタビューが完了しました。ありがとうございました。", state
    else:
        next_question = generate_interview_questions(response_text, state, first_task)
        return next_question, state


# インタビューを実行する関数
def run_interview():
    # 各側面のカバー状態と質問回数を管理するフラグ
    state = {
        "covered": {"action": False, "cognition": False, "information": False},
        "count": {
            "action": 0,  # 行動に関する質問回数
            "cognition": 0,  # 認知に関する質問回数
            "information": 0,  # 情報に関する質問回数
        },
    }

    # 最初の質問と回答を一回だけ受け取る
    print("質問: 今何の作業をしているのですか？")
    first_task = input("\nインタビュイーの回答: ")  # 最初の作業を記録

    # 最初の回答に基づいてインタビューを開始
    response_text = first_task  # 最初の回答を設定

    while True:
        # 回答を分析し、次の質問を生成
        analysis, state = analyze_response(response_text, state)
        print(f"\n回答の分析結果: {analysis}")

        # 全ての要素がカバーされたかをチェック
        if check_completion(state) == True:  # 全ての要素がTrueであればインタビューを終了
            print("\nインタビューが完了しました。ありがとうございました。")
            break

        # 次の質問を決定（最初の作業に基づく質問）
        next_question, state = manage_interview_flow(response_text, state, first_task)
        print(f"\n次の質問: {next_question}")

        # 次の回答を受け取る
        response_text = input("\nインタビュイーの回答: ")


# インタビューを開始
run_interview()
