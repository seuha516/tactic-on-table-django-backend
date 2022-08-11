import json, bcrypt, jwt, os
from django.db import connection
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from .models import Account

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            if data['username'] == '':
                return JsonResponse({"message": "사용할 ID를 입력해 주세요."}, status=401)
            if data['password'] == '':
                return JsonResponse({"message": "사용할 비밀번호를 입력해 주세요."}, status=401)
            if data['email'] == '':
                return JsonResponse({"message": "사용할 이메일을 입력해 주세요."}, status=401)
            if data['nickname'] == '':
                return JsonResponse({"message": "사용할 닉네임을 입력해 주세요."}, status=401)
            if data['nickname'][0:2] == '익명':
                return JsonResponse({"message": "닉네임을 \"익명\"으로 시작하게 만들 수 없습니다."}, status=400)
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

            token = jwt.encode({'username': data['username']},
                               os.environ.get("JWT_SECRET"),
                               os.environ.get("ALGORITHM"))
            response = JsonResponse({"username": data['username'],
                                     "nickname": data['nickname'],
                                     "email": data['email'],
                                     "image": 'profile_default.png'},
                                    status=200);
            response.set_cookie('access_token', token, max_age=60*60*24*7, samesite='None', secure=True, httponly=True)
            return response

        except Exception:
            return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            if data['username'] == "":
                return JsonResponse({"message": "ID를 입력하세요."}, status=401)
            if data['password'] == "":
                return JsonResponse({"message": "비밀번호를 입력하세요."}, status=401)
            if not (Account.objects.filter(username=data['username'])).exists():
                return JsonResponse({"message": "존재하지 않는 ID입니다."}, status=401)

            account = Account.objects.get(username=data['username'])
            if bcrypt.checkpw(data['password'].encode('utf-8'), account.hashed_password.encode('utf-8')):
                token = jwt.encode({'username': data['username']},
                                   os.environ.get("JWT_SECRET"),
                                   os.environ.get("ALGORITHM"))
                response = JsonResponse({"username": account.username,
                                         "nickname": account.nickname,
                                         "email": account.email,
                                         "image": account.image},
                                        status=200);
                response.set_cookie('access_token', token, max_age=60*60*24*7, samesite='None', secure=True, httponly=True)
                return response
            else:
                return JsonResponse({"message": "비밀번호가 틀렸습니다."}, status=401)

        except Exception:
            return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

@csrf_exempt
def check(request):
    if request.method == 'GET':
        return HttpResponse(status=200)
    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

@csrf_exempt
def logout(request):
    if request.method == 'GET':
        response = HttpResponse(status=204)
        response.set_cookie('access_token', None, max_age=60*60*24*7, samesite='None', secure=True, httponly=True)
        return response
    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

@csrf_exempt
def user(request):
    try:
        if request.method == 'GET':
            username = request.GET.get('username', '')
            if not (Account.objects.filter(username=username)).exists():
                return JsonResponse({"message": "존재하지 않는 유저입니다."}, status=404)
            account = Account.objects.get(username=username)

            cursor = connection.cursor()
            strSQL = "SELECT `num`, `game`, `players`, `result`, `date` FROM match_record WHERE %s MEMBER OF( players ) ORDER BY date DESC" \
                     % ('\"%s\"' % username)
            cursor.execute(strSQL)
            sqlData = cursor.fetchall()
            connection.close()

            user_record = []
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
                user_record.append(obj)

            return JsonResponse({
                'username': account.username,
                'email': account.email,
                'nickname': account.nickname,
                'image': account.image,
                'total_score': account.total_score,
                'score': account.score,
                'user_record': user_record
            }, status=200)

        elif request.method == 'PATCH':
            data = JSONParser().parse(request)
            username = data['username']
            if not (Account.objects.filter(username=username)).exists():
                return JsonResponse({"message": "존재하지 않는 유저입니다."}, status=404)

            account = Account.objects.get(username=username)
            if not bcrypt.checkpw(data['originalPassword'].encode('utf-8'), account.hashed_password.encode('utf-8')):
                return JsonResponse({"message": "비밀번호가 틀립니다."}, status=400)

            if data['email'] == '':
                return JsonResponse({"message": "이메일을 입력해야 합니다."}, status=401)
            if data['nickname'] == '':
                return JsonResponse({"message": "닉네임을 입력해야 합니다."}, status=401)
            if (Account.objects.filter(nickname=data['nickname'])).exists():
                if account.nickname != data['nickname']:
                    return JsonResponse({"message": "이미 있는 닉네임입니다."}, status=409)
            if data['nickname'][0:2] == '익명':
                return JsonResponse({"message": "닉네임을 \"익명\"으로 시작하게 만들 수 없습니다."}, status=400)

            if data['password']:
                hashedPassword = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                Account.objects.filter(username=username).update(
                    hashed_password=hashedPassword,
                    email=data['email'],
                    nickname=data['nickname'],
                    image=data['image'],
                )
            else:
                Account.objects.filter(username=username).update(
                    email=data['email'],
                    nickname=data['nickname'],
                    image=data['image'],
                )

            response = JsonResponse({"username": data['username'],
                                     "nickname": data['nickname'],
                                     "email": data['email'],
                                     "image": data['image']},
                                    status=200);
            return response

        elif request.method == 'POST':
            data = JSONParser().parse(request)
            username = data['username']
            if not (Account.objects.filter(username=username)).exists():
                return JsonResponse({"message": "존재하지 않는 유저입니다."}, status=404)

            account = Account.objects.get(username=username)
            if bcrypt.checkpw(data['originalPassword'].encode('utf-8'), account.hashed_password.encode('utf-8')):
                account.delete()
                return HttpResponse(status=200)
            else:
                return JsonResponse({"message": "비밀번호가 틀립니다."}, status=400)

        else:
            return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

    except Exception:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

@csrf_exempt
def record(request):
    if request.method == 'GET':
        try:
            page = request.GET.get('page', '1')
            if not page.isdigit():
                return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)
            page = int(page)
            if page < 1:
                return JsonResponse({"message": "페이지가 잘못되었습니다."}, status=500)

            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM match_record")
            count = cursor.fetchall()
            strSQL = "SELECT `num`, `game`, `players`, `result`, `date` FROM match_record ORDER BY date DESC LIMIT %d, %d" \
                     % ((page - 1) * 10, 10)
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

        except Exception:
            return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

@csrf_exempt
def ranking(request):
    if request.method == 'GET':
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

        except Exception:
            return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

    else:
        return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)
