import google.generativeai as genai
import PIL.Image
import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# img = PIL.Image.open('path/to/image.png')

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
# response = model.generate_content(["What is in this photo?", img])
response = model.generate_content(["日本の首都は？"])
print(response.text)