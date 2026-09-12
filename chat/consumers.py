import json, datetime
from http.cookies import SimpleCookie
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from copy import deepcopy

from room.models import Room
from account.models import Account
from account.models import MatchRecord
from utils.jwtMiddleware import decode_jwt

from utils.chess import ChessBoard, COLOR, MOVE, PIECE

def recordUpdate(game, players, result):
    MatchRecord(
        game=game,
        players=players,
        result=result,
        date=datetime.datetime.now(),
    ).save()
def winnerUpdate(game, username):
    if (Account.objects.filter(username=username)).exists():
        account = Account.objects.get(username=username)
        account.total_score += 1
        account.score[game] += 1
        account.save()

class ChatConsumer(AsyncJsonWebsocketConsumer):

    def get_authenticated_account(self):
        cookies = SimpleCookie()
        for header, value in self.scope.get('headers', []):
            if header == b'cookie':
                cookies.load(value.decode('utf-8'))
                break
        access_token = cookies.get('access_token')
        if access_token is None:
            return None
        try:
            username = decode_jwt(access_token.value).get('username')
            return Account.objects.get(username=username)
        except Exception:
            return None

    async def connect(self):
        code = self.scope['url_route']['kwargs']['code']
        password = self.scope['url_route']['kwargs'].get('password', '')
        self.code = code
        self.hasInfo = False
        self.account = self.get_authenticated_account()
        await self.accept()

        if code != 'lobby':
            if self.account is None:
                await self.send(text_data=json.dumps({'type': 'KICK', 'value': '로그인이 필요합니다.'}))
                await self.close()
                return
            if not (Room.objects.filter(code=code)).exists():
                await self.send(text_data=json.dumps({
                    'type': 'KICK',
                    'value': '존재하지 않는 방입니다.'
                }))
                await self.close()
                return
            else:
                room = Room.objects.get(code=code)
                if room.password != password:
                    await self.send(text_data=json.dumps({
                        'type': 'KICK',
                        'value': '비밀번호가 틀렸습니다.'
                    }))
                    await self.close()
                    return
                if len(room.players) + 1 > room.max_player:
                    await self.send(text_data=json.dumps({
                        'type': 'KICK',
                        'value': '인원이 가득 찼습니다.'
                    }))
                    await self.close()
                    return

                self.pending_player = {'pending': self.channel_name}
                room.players.append(self.pending_player)
                room.save()

                await self.send(text_data=json.dumps({'type': 'JOIN'}))
                await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})

        await self.channel_layer.group_add(self.code, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.code, self.channel_name)

        if self.code != 'lobby':
            if not self.hasInfo:
                room = Room.objects.filter(code=self.code).first()
                if room and hasattr(self, 'pending_player') and self.pending_player in room.players:
                    room.players.remove(self.pending_player)
                    room.save()
                return

            room = Room.objects.get(code=self.code)
            players = room.players
            for i in range(len(players)):
                if players[i].get('username', '') == self.username:
                    del players[i]
                    room.players = players
                    room.save()
                    if len(players) == 0:
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

            # 게임 중 연결 끊김
            if room.status == 1:
                room.status = 0
                room.save()
                await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})

                # 체스
                if room.game == 0 and len(players) > 0:
                    # 게임 로드, 메시지 전송
                    game = ChessBoard()
                    game.setting(json.loads(room.data))
                    data = game.getData()
                    del data['message']
                    winner = players[0]
                    await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                        'type': 'CHATTING',
                        'value': {
                            'type': 'GAME',
                            'info': 'RESULT',
                            'content': '접속 종료로 인해 %s님이 승리했습니다.' % winner['nickname']
                        }
                    }})

                    # 전적 업로드
                    recordResult = {'type': '1on1', 'winner': winner['username']}
                    recordPlayers = []
                    for i in range(len(game.players)):
                        recordPlayers.append(game.players[i]['username'])
                    recordUpdate(0, recordPlayers, recordResult)
                    winnerUpdate(0, winner['username'])

                    # result 작성, 전달
                    data['result'] = {'winner': players[0]}
                    await self.channel_layer.group_send(self.code, {'type': 'sendChess', 'data': data})
                # TODO 3인 이상 게임일 때 대책 필요


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        function_name = text_data_json['function']
        data = text_data_json['data']

        if self.code != 'lobby' and not self.hasInfo and function_name != 'joinRoom':
            return
        if function_name == 'joinRoom' and self.code != 'lobby' and not self.hasInfo:
            await self.joinRoom()
        elif function_name == 'chatting' and (self.hasInfo or (self.code == 'lobby' and self.account is not None)) and isinstance(data, dict):
            data['user'] = {'username': self.account.username, 'nickname': self.account.nickname, 'image': self.account.image}
            await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {'type': 'CHATTING', 'value': data}})
        elif function_name == 'ready' and self.hasInfo:
            await self.ready()
        elif function_name == 'chessMove' and self.hasInfo:
            await self.chessMove(data)

    async def sendData(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def joinRoom(self):
        room = Room.objects.get(code=self.code)
        players = room.players

        dummyIndex = None
        duplicated = False
        for i in range(len(players)):
            if players[i] == self.pending_player:
                dummyIndex = i
            elif players[i].get('username') == self.account.username:
                duplicated = True

        self.hasInfo = False
        if duplicated or dummyIndex is None:
            if dummyIndex is not None:
                del players[dummyIndex]
            room.players = players
            room.save()
            await self.send(text_data=json.dumps({
                'type': 'KICK',
                'value': '중복 접속이 감지되었습니다.'
            }))
            await self.close()
            return

        players[dummyIndex] = {'username': self.account.username, 'nickname': self.account.nickname, 'image': self.account.image}
        players[dummyIndex]['ready'] = False
        room.players = players
        room.save()
        self.hasInfo = True

        self.username = self.account.username
        self.nickname = self.account.nickname
        self.image = self.account.image

        await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
            'type': 'ROOM',
            'value': {
                'name': room.name,
                'game': room.game,
                'maxPlayer': room.max_player,
                'players': room.players
            }
        }})
        await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
            'type': 'CHATTING',
            'value': {
                'type': 'NOTICE',
                'info': 'JOIN',
                'content': self.nickname + ' 님이 참가했습니다.'
            }
        }})

    async def ready(self):
        room = Room.objects.get(code=self.code)
        players = room.players

        # ready 적용
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
            # ready 초기화
            for i in range(len(players)):
                players[i]['ready'] = False
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

            # 게임 세팅
            # 체스
            if room.game == 0:
                gamePlayers = deepcopy(room.players)
                game = ChessBoard(gamePlayers)
                room.status = 1
                room.data = json.dumps(game.getSave(), ensure_ascii=False)
                room.save()
                await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})
                await self.channel_layer.group_send(self.code, {'type': 'sendChess', 'data': game.getData()})
                await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': {
                    'type': 'CHATTING',
                    'value': {
                        'type': 'GAME',
                        'info': 'RESULT',
                        'content': '게임을 시작합니다!'
                    }
                }})

    async def sendChess(self, event):
        data = deepcopy(event['data'])

        idx = 0 if data['players'][0]['username'] == self.username else 1
        data['myColor'] = data['players'][idx]['color']

        if data['players'][idx]['color'] == 1:
            data['board'].reverse()
            data['moveable'].reverse()
            for i in range(8):
                for j in range(8):
                    data['moveable'][i][j].reverse()
            data['lastMove'][0]['x'] = 7 - data['lastMove'][0]['x']
            data['lastMove'][1]['x'] = 7 - data['lastMove'][1]['x']
        if idx == 1:
            data['players'].reverse()

        await self.send(text_data=json.dumps({
            'type': 'GAME',
            'value': data
        }))

    async def chessMove(self, data):
        # 로드
        room = Room.objects.get(code=self.code)
        game = ChessBoard()
        game.setting(json.loads(room.data))

        if not any(player['username'] == self.username and player['color'] == game.turn for player in game.players):
            return

        try:
            ox = data['originalLocation']['x']
            oy = data['originalLocation']['y']
            tx = data['targetLocation']['x']
            ty = data['targetLocation']['y']
            if not all(isinstance(value, int) and 0 <= value < 8 for value in [ox, oy, tx, ty]):
                return
            if game.turn == COLOR.BLACK:
                ox, tx = 7 - ox, 7 - tx
            piece = game.board[ox][oy]
            move_type = game.getLegalMoveList(piece)[tx][ty] if piece else None
            if move_type is None:
                return
            if move_type == MOVE.PROMOTION and data.get('piece') not in [PIECE.KNIGHT, PIECE.BISHOP, PIECE.ROOK, PIECE.QUEEN]:
                return
            data['moveType'] = move_type
        except (KeyError, TypeError):
            return

        # 이동
        game.move(data)
        room.data = json.dumps(game.getSave(), ensure_ascii=False)
        room.save()

        # 게임 상태 체크
        data = game.getData()
        if data['message']:
            await self.channel_layer.group_send(self.code, {'type': 'sendData', 'data': data['message']})
        del data['message']

        if data['result']:
            room.status = 0
            room.save()
            await self.channel_layer.group_send('lobby', {'type': 'sendData', 'data': {'type': 'LOBBY_UPDATE'}})

            recordResult = data['result']['recordResult']
            players = []
            for i in range(len(game.players)):
                players.append(game.players[i]['username'])
            recordUpdate(0, players, recordResult)
            del data['result']['recordResult']
            if data['result']['winner']:
                winnerUpdate(0, data['result']['winner']['username'])

        await self.channel_layer.group_send(self.code, {'type': 'sendChess', 'data': data})
