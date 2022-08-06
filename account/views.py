import json, bcrypt, jwt, os
from django.http import JsonResponse
from django.db import connection
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from .models import Account

@csrf_exempt
def signup(request):
    data = JSONParser().parse(request)
    try:
        if data['username'] == '':
            return JsonResponse({"message": "사용할 ID를 입력해 주세요."}, status=401)
        if data['password'] == '':
            return JsonResponse({"message": "사용할 비밀번호를 입력해 주세요."}, status=401)
        if data['email'] == '':
            return JsonResponse({"message": "사용할 이메일을 입력해 주세요."}, status=401)
        if data['nickname'] == '':
            return JsonResponse({"message": "사용할 닉네임을 입력해 주세요."}, status=401)
        if (Account.objects.filter(username=data['username'])).exists():
            return JsonResponse({"message": "이미 있는 ID입니다."}, status=409)
        if (Account.objects.filter(nickname=data['nickname'])).exists():
            return JsonResponse({"message": "이미 있는 닉네임입니다."}, status=409)

        hashedPassword = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        Account(
            username=data['username'],
            hashed_password=hashedPassword,
            email=data['email'],
            nickname=data['nickname'],
            image="profile_default.png",
            total_score=0,
            score=[0,0,0,0,0,0,0,0,0,0,0,0]
        ).save()

        # token = jwt.encode({'username': data['username']}, os.environ.get("JWT_SECRET"),
        #                    os.environ.get("ALGORITHM"))
        response = JsonResponse({"username": data['username'],
                                 "nickname": data['nickname'],
                                 "image": 'profile_default.png'},
                                status=200);
        return response

    except KeyError:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

@csrf_exempt
def login(request):
    data = JSONParser().parse(request)
    try:
        if data['username'] == "":
            return JsonResponse({"message": "ID를 입력하세요."}, status=401)
        if data['password'] == "":
            return JsonResponse({"message": "비밀번호를 입력하세요."}, status=401)
        if not (Account.objects.filter(username=data['username'])).exists():
            return JsonResponse({"message": "존재하지 않는 ID입니다."}, status=401)

        user = Account.objects.get(username=data['username'])
        if bcrypt.checkpw(data['password'].encode('utf-8'), user.hashedPassword.encode('utf-8')):
            token = jwt.encode({'username': data['username']}, os.environ.get("JWT_SECRET"),
                               os.environ.get("ALGORITHM")).decode('utf-8')
            response = JsonResponse({"username": user.username, "email": user.email, "nickname": user.nickname,
                                     "setting": user.setting, "notice": user.notice, "token": token}, status=200);
            return response
        else:
            return JsonResponse({"message": "비밀번호가 틀렸습니다."}, status=401)

    except KeyError:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

@csrf_exempt
def ranking(request):
    try:
        page = request.GET.get('page', '1')
        if not page.isdigit():
            return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)
        page = int(page)
        if page < 1:
            return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM account")
        count = cursor.fetchall()
        strSQL = "SELECT `username`, `nickname`, `image`, `total_score`, `score` FROM account ORDER BY total_score DESC LIMIT %d, %d" \
                 % ((page - 1) * 10, 10)
        cursor.execute(strSQL)
        sqlData = cursor.fetchall()
        connection.close()

        result = []
        for x in sqlData:
            obj = {
                'username': x[0],
                'nickname': x[1],
                'image': x[2],
                'total_score': x[3],
                'score': json.loads(x[4]),
            }
            result.append(obj)

        return JsonResponse({"result": result, "count": count[0][0]}, status=200)

    except KeyError:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

@csrf_exempt
def record(request):
    try:
        page = request.GET.get('page', '1')
        if not page.isdigit():
            return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)
        page = int(page)
        if page < 1:
            return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)

        username = request.GET.get('username', '')

        cursor = connection.cursor()
        if username == '':
            cursor.execute("SELECT COUNT(*) FROM match_record")
            count = cursor.fetchall()
            strSQL = "SELECT `num`, `game`, `players`, `result`, `date` FROM match_record ORDER BY date DESC LIMIT %d, %d" \
                 % ((page - 1) * 10, 10)
        else:
            cursor.execute("SELECT COUNT(*) FROM match_record WHERE %s MEMBER OF( players )" % ('\"%s\"' % username))
            count = cursor.fetchall()
            strSQL = "SELECT `num`, `game`, `players`, `result`, `date` FROM match_record WHERE %s MEMBER OF( players ) ORDER BY date DESC LIMIT %d, %d" \
                     % ('\"%s\"' % username, (page - 1) * 10, 10)
        cursor.execute(strSQL)
        sqlData = cursor.fetchall()
        connection.close()

        result = []
        for x in sqlData:
            recordPlayers = []
            for playerUsername in json.loads(x[2]):
                player = Account.objects.get(username=playerUsername)
                recordPlayers.append({
                    'username': player.username,
                    'nickname': player.nickname,
                    'image': player.image,
                })

            recordResult = json.loads(x[3])
            winnerUsername = recordResult.get('winner', None)
            if winnerUsername is not None:
                player = Account.objects.get(username=winnerUsername)
                recordResult['winner'] = {
                    'username': player.username,
                    'nickname': player.nickname,
                    'image': player.image,
                }

            obj = {
                'num': x[0],
                'game': x[1],
                'players': recordPlayers,
                'result': recordResult,
                'date': x[4],
            }
            result.append(obj)

        return JsonResponse({"result": result, "count": count[0][0]}, status=200)

    except KeyError:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)