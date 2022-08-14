from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from account.models import Account
from room.models import Room

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['code']
        self.room_group_name = 'chat_%s' % self.room_name

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
        text_data_json = json.loads(text_data)
        function_name = text_data_json['type']
        data = text_data_json['data']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': function_name,
                'data': data
            }
        )

    async def chatting(self, event):
        data = event['data']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'value': data
        }))

    async def tryJoinRoom(self, event):
        data = event['data']
        # if not (Room.objects.filter(code=data['code'])).exists():
        #     await self.send(text_data=json.dumps({
        #         'type': 'game',
        #         'value': '존재하지 않는 방입니다.'
        #     }))
        print('>>>' + data['code'])
        account = Account.objects.get(username="user1")
        print(account.nickname)
        room = Room.objects.filter(code=data['code'])[0]
        print(room.name)


