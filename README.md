# flask_gpt4o

## setup

1. install dependencies
   ```bash
   pip install -r requirements.txt
   ```
2. add .env file
   ```bash
   OPENAI_API_KEY=YOUR_API_KEY
   LINE_CHANNEL_ACCESS_TOKEN=YOUR_ACCESS_TOKEN
   GEMINI_API_KEY=YOUR_API_KEY
   MONGODB_USERNAME=admin
   MONGODB_PASSWORD=admin
   ```

## run

- local

  you can use .env file to set the environment variables

  ```bash
  python app.py --load_env
  ```

- render.com

  you must set environment variables in the render.com dashboard

  ```bash
  python app.py
  ```
