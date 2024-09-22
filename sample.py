# http://127.0.0.1:3011に以下を送信
# {
#   "destination": "xxxxxxxxxx",
#   "events": [
#     {
#       "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
#       "type": "message",
#       "mode": "active",
#       "timestamp": 1462629479859,
#       "source": {
#         "type": "group",
#         "groupId": "Ca56f94637c...",
#         "userId": "U4af4980629..."
#       },
#       "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",
#       "deliveryContext": {
#         "isRedelivery": false
#       },
#       "message": {
#         "id": "444573844083572737",
#         "type": "text",
#         "quoteToken": "q3Plxr4AgKd...",
#         "text": "@All @example Good Morning!! (love)",
#         "emojis": [
#           {
#             "index": 29,
#             "length": 6,
#             "productId": "5ac1bfd5040ab15980c9b435",
#             "emojiId": "001"
#           }
#         ],
#         "mention": {
#           "mentionees": [
#             {
#               "index": 0,
#               "length": 4,
#               "type": "all"
#             },
#             {
#               "index": 5,
#               "length": 8,
#               "userId": "U49585cd0d5...",
#               "type": "user"
#             }
#           ]
#         }
#       }
#     }
#   ]
# }

import json

import requests

send_data = {
    "destination": "xxxxxxxxxx",
    "events": [
        {
            "replyToken": "nHuyWiB7yP5Zw52FIkcQobQuGDXCTA",
            "type": "message",
            "mode": "active",
            "timestamp": 1462629479859,
            "source": {
                "type": "group",
                "groupId": "Ca56f94637c...",
                "userId": "Uaedb10ed004057a7f73606b62ecfc6f7",
            },
            "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",
            "deliveryContext": {"isRedelivery": False},
            "message": {
                "id": "444573844083572737",
                "type": "text",
                "quoteToken": "q3Plxr4AgKd...",
                "text": "プログラミングをしています",
                "emojis": [
                    {
                        "index": 29,
                        "length": 6,
                        "productId": "5ac1bfd5040ab15980c9b435",
                        "emojiId": "001",
                    }
                ],
                "mention": {
                    "mentionees": [
                        {"index": 0, "length": 4, "type": "all"},
                        {
                            "index": 5,
                            "length": 8,
                            "userId": "U49585cd0d5...",
                            "type": "user",
                        },
                    ]
                },
            },
        }
    ],
}

response = requests.post(
    "http://127.0.0.1:3011/callback",
    headers={"Content-Type": "application/json"},
    data=json.dumps(send_data),
)

print(response.text)
