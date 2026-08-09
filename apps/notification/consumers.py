import json
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(WebsocketConsumer):

    def connect(self):

        
        # READ HEADERS
        query_string = self.scope["query_string"].decode()

        params = parse_qs(query_string)

        token = params.get("token", [None])[0]

        if not token:
            self.close()
            return

        
        # DECODE TOKEN
        try:
            access_token = AccessToken(token)

            user_id = access_token["user_id"]

            self.user = User.objects.select_related("account").get(
                id=user_id
            )
            

        except Exception as e:
            print(e)
            self.close()
            return

        
        # PERSONAL GROUP
        self.personal_group = f"user_{self.user.account.id}"

        async_to_sync(
            self.channel_layer.group_add
        )(
            self.personal_group,
            self.channel_name
        )

        print(f"Joined -> {self.personal_group}")

       
        # CUSTOMER GROUP
        if self.user.role == "customer":

            async_to_sync(
                self.channel_layer.group_add
            )(
                "customers",
                self.channel_name
            )

            print("Joined -> customers")

        
        # SELLER GROUP
        elif self.user.role == "seller":

            seller_group = f"seller_{self.user.account.id}"

            async_to_sync(
                self.channel_layer.group_add
            )(
                seller_group,
                self.channel_name
            )

            print(f"Joined -> {seller_group}")

        
        # ADMIN GROUP
        elif self.user.role == "admin":

            async_to_sync(
                self.channel_layer.group_add
            )(
                "admins",
                self.channel_name
            )

            print("Joined -> admins")

        
        # ACCEP CONNECTION
        self.accept()

        self.send(
            text_data=json.dumps({
                "type": "connected",
                "user": self.user.email,
            })
        )
    
    # SEND NOTIFICATION
    def send_notification(self, event):
        
        print("=" * 60)
        print("Notification received in Consumer")
        print(event)
        print("=" * 60)
    
        self.send(
            text_data=json.dumps({
                "type": "notification",
                "notification": event["notification"],
            })
        )



    # USER DISCONNECT
    def disconnect(self, close_code):

        if hasattr(self, "personal_group"):

            async_to_sync(
                self.channel_layer.group_discard
            )(
                self.personal_group,
                self.channel_name
            )

        if getattr(self.user, "role", None) == "customer":

            async_to_sync(
                self.channel_layer.group_discard
            )(
                "customers",
                self.channel_name
            )

        elif getattr(self.user, "role", None) == "seller":

            async_to_sync(
                self.channel_layer.group_discard
            )(
                f"seller_{self.user.account.id}",
                self.channel_name
            )

        elif getattr(self.user, "role", None) == "admin":

            async_to_sync(
                self.channel_layer.group_discard
            )(
                "admins",
                self.channel_name
            )

        print("Disconnected")

    def receive(self, text_data):
        pass