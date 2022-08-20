from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from room.models import Room
from utils.chess import ChessBoard


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        code = self.scope['url_route']['kwargs']['code']
        password = self.scope['url_route']['kwargs'].get('password', '')
        self.code = code

        await self.channel_layer.group_add(self.code, self.channel_name)
        await self.accept()

        if code != 'lobby':
            if not (Room.objects.filter(code=code)).exists():
                await self.send(text_data=json.dumps({
                    'type': 'KICK',
                    'value': '존재하지 않는 방입니다.'
                }))
                return
            else:
                room = Room.objects.get(code=code)
                if room.password != password:
                    await self.send(text_data=json.dumps({
                        'type': 'KICK',
                        'value': '비밀번호가 틀렸습니다.'
                    }))
                    return
                if len(room.players) + 1 > room.max_player:
                    await self.send(text_data=json.dumps({
                        'type': 'KICK',
                        'value': '인원이 가득 찼습니다.'
                    }))
                    return

                room.players.append('dummy')
                room.save()

                await self.send(text_data=json.dumps({'type': 'JOIN'}))
                await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.code, self.channel_name)

        if self.code != 'lobby':
            if not self.hasInfo:
                return

            room = Room.objects.get(code=self.code)
            players = room.players
            for i in range(len(players)):
                if players[i].get('username', '') == self.username:
                    del players[i]
                    room.players = players
                    room.save()
                    if len(room.players) == 0:
                        room.delete()
                    else:
                        await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                            'type': 'ROOM',
                            'value': {
                                'name': room.name,
                                'game': room.game,
                                'maxPlayer': room.max_player,
                                'players': room.players
                            }
                        }})
                    break

            await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                'type': 'CHATTING',
                'value': {
                    'type': 'NOTICE',
                    'info': 'LEAVE',
                    'content': self.nickname + ' 님이 떠났습니다.'
                }
            }})
            await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        function_name = text_data_json['function']
        data = text_data_json['data']

        if function_name == 'joinRoom':
            room = Room.objects.get(code=self.code)
            players = room.players

            dummyIndex = 0
            duplicated = False
            for i in range(len(players)):
                if players[i] == 'dummy':
                    dummyIndex = i
                elif players[i]['username'] == data['username']:
                    duplicated = True

            self.hasInfo = False
            if duplicated:
                del players[dummyIndex]
                room.players = players
                room.save()
                await self.send(text_data=json.dumps({
                    'type': 'KICK',
                    'value': '중복 접속이 감지되었습니다.'
                }))
                return

            players[dummyIndex] = data
            players[dummyIndex]['ready'] = False
            room.players = players
            room.save()
            self.hasInfo = True

            self.username = data['username']
            self.nickname = data['nickname']

            await self.channel_layer.group_send(self.code, {'type': 'joinRoom', 'nickname': self.nickname, 'room': {
                'name': room.name,
                'game': room.game,
                'maxPlayer': room.max_player,
                'players': room.players
            }})

            return
        if function_name == 'ready':
            room = Room.objects.get(code=self.code)
            players = room.players

            start = (len(players) == room.max_player)
            for i in range(len(players)):
                if players[i].get('username', '') == self.username:
                    players[i]['ready'] = True
                    room.players = players
                    room.save()
                    await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                        'type': 'ROOM',
                        'value': {
                            'name': room.name,
                            'game': room.game,
                            'maxPlayer': room.max_player,
                            'players': room.players
                        }
                    }})
                elif not players[i].get('ready', False):
                    start = False

            if start:
                self.game = ChessBoard(room.players[0]['username'], room.players[1]['username'])
                room.status = 1
                await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})
                await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                    'type': 'GAME',
                    'value': self.game.getData()
                }})

            return

        await self.channel_layer.group_send(self.code, {'type': function_name, 'data': data})

    async def sendData(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def chatting(self, event):
        await self.send(text_data=json.dumps({'type': 'CHATTING', 'value': event['data']}))

    async def joinRoom(self, event):
        nickname = event['nickname']
        room = event['room']

        await self.send(text_data=json.dumps({
            'type': 'ROOM',
            'value': room
        }))
        await self.send(text_data=json.dumps({
            'type': 'CHATTING',
            'value': {
                'type': 'NOTICE',
                'info': 'JOIN',
                'content': nickname + ' 님이 참가했습니다.'
            }
        }))

    async def chessMove(self, event):
        print(event['data'])