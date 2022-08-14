import json
from django.db import connection
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt

from .models import GameRoom
from utils.getRandom import makeRandomString, makeRandomColor

@csrf_exempt
def index(request):
    try:
        if request.method == 'GET':
            cursor = connection.cursor()
            strSQL = "SELECT `num`, `code`, `name`, `password`, `color`, " \
                     "`game`, `max_player`, `players` FROM room ORDER BY num"
            cursor.execute(strSQL)
            sqlData = cursor.fetchall()
            connection.close()

            result = []
            for x in sqlData:
                obj = {
                    'num': x[0],
                    'code': x[1],
                    'name': x[2],
                    'lock': False if x[3] == '' else True,
                    'color': x[4],
                    'game': x[5],
                    'maxPlayer': x[6],
                    'players': len(json.loads(x[7])),
                }
                result.append(obj)

            return JsonResponse({"result": result}, status=200)

        elif request.method == 'POST':
            data = JSONParser().parse(request)

            while True:
                code = makeRandomString(16)
                if not GameRoom.objects.filter(code=code).exists():
                    break

            GameRoom(
                code=code,
                name=data['name'],
                password=data['password'],
                color=makeRandomColor(),
                game=data['game'],
                max_player=data['maxPlayer'],
                players=[]
            ).save()

            return JsonResponse({"code": code}, status=200)

        else:
            return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

    except Exception:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

@csrf_exempt
def update(request, code):
    try:
        if request.method == 'POST':
            print('방 업데이트. 코드는' + code)
            return JsonResponse({"message": "ok"}, status=200)

        else:
            return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=500)

    except Exception:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)

