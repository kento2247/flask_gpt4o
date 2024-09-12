# flask_gpt4o

## setup
1. clone repository
   ```sh
   git clone git@github.com:kento2247/flask_gpt4o.git
   cd flask_gpt4o
   ```

2. install dependencies
   ```sh
   pip install -r requirements.txt
   ```
3. add .env file
   ```sh
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
