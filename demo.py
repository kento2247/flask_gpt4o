import requests

endpoint = "http://192.168.0.12:3011/callback"
data = {
    "destination": "xxxxxxxxxx",
    "events": [
        {
            "replyToken": "85cbe770fa8b4f45bbe077b1d4be4a36",
            "type": "follow",
            "mode": "active",
            "timestamp": 1705891467176,
            "source": {"type": "user", "userId": "Uaedb10ed004057a7f73606b62ecfc6f7"},
            "webhookEventId": "01HMQGW40RZJPJM3RAJP7BHC2Q",
            "deliveryContext": {"isRedelivery": False},
            "follow": {"isUnblocked": False},
        }
    ],
}

response = requests.post(endpoint, json=data)
print(response.text)
