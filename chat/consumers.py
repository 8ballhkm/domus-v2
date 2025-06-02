import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        User = get_user_model()
        self.user = self.scope['user']
        print("Connecting user:", self.user, "Authenticated?", self.user.is_authenticated)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        user_ids = self.room_name.split('_')
        sender_id = self.user.id
        receiver_id = int(user_ids[0]) if sender_id != int(user_ids[0]) else int(user_ids[1])

        await self.save_message(sender_id, receiver_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f'{self.user.username}: {message}',
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        from django.apps import apps
        User = get_user_model()
        Message = apps.get_model('chat', 'Message')
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)
        Message.objects.create(sender=sender, receiver=receiver, content=content)
