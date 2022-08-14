import jwt, os
from http import HTTPStatus
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from jwt.exceptions import ExpiredSignatureError

from account.models import Account


def decode_jwt(access_token):
    return jwt.decode(
        access_token,
        os.environ.get("JWT_SECRET"),
        os.environ.get("ALGORITHM")
    )

class JsonWebTokenMiddleWare(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if (
                    (request.path[:7] == "/media/" and request.method == "POST")
                    or (request.path == "/account/check/")
                    or ((request.path == "/account/user" or request.path == "/account/user/") and request.method != "GET")
            ):
                access_token = request.COOKIES.get("access_token", None)
                if not access_token:
                    raise PermissionDenied()

                payload = decode_jwt(access_token)
                username = payload.get("username", None)
                if not username:
                    raise PermissionDenied()

                Account.objects.get(username=username)

            return self.get_response(request)

        except (PermissionDenied, Account.DoesNotExist):
            return JsonResponse({"message": "토큰이 올바르지 않습니다."}, status=HTTPStatus.UNAUTHORIZED)

        except ExpiredSignatureError:
            return JsonResponse({"message": "토큰이 만료되었습니다."}, status=HTTPStatus.FORBIDDEN)