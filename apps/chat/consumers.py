from channels.generic.websocket import WebsocketConsumer
import json
from channels.generic.websocket import WebsocketConsumer
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from apps.user.models import User


# CHAT CONSUMER
class ChatConsumer(WebsocketConsumer):

    def connect(self):

        # URL: /ws/chat/15/
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        print("=" * 60)
        print("CHAT CONNECTED")
        print(f"Conversation : {self.conversation_id}")
        print(f"Channel Name : {self.channel_name}")
        print("=" * 60)

        self.accept()

        self.send(
            text_data=json.dumps({
                "type": "connection",
                "message": "Connected successfully.",
                "conversation_id": self.conversation_id,
            })
        )

    def receive(self, text_data):

        data = json.loads(text_data)

        print("=" * 60)
        print("MESSAGE RECEIVED")
        print(data)
        print("=" * 60)

        self.send(
            text_data=json.dumps({
                "type": "echo",
                "conversation_id": self.conversation_id,
                "data": data,
            })
        )

    def disconnect(self, close_code):

        print("=" * 60)
        print("CHAT DISCONNECTED")
        print(f"Conversation : {self.conversation_id}")
        print(f"Close Code   : {close_code}")
        print("=" * 60)