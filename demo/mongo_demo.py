import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

load_dotenv()


def main():
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    uri = f"mongodb+srv://{username}:{password}@gpt4otest.aartxch.mongodb.net/?retryWrites=true&w=majority&appName=gpt4otest"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Create a new database
    db = client["gpt4otest"]
    # Create a new collection
    collection = db["test"]

    data = {
        "userid": "demo",
        "session_id": "test",
        "data": [
            {"role": "user", "content": "test"},
            {"role": "assistant", "content": "test"},
        ],
    }
    # Insert a new document
    # collection.insert_one({"name": "test"})
    # collection.insert_one(data)

    # Find the document
    # document = collection.find_one({"name": "test"})

    # userid = "demo"かつsession_id = "demo"のデータを取得
    document = collection.find_one({"userid": "demo", "session_id": "do"})
    print(document)


if __name__ == "__main__":
    main()
