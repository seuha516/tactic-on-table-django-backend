from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

from utils.getRandom import makeRandomString

@csrf_exempt
def upload(request):
    try:
        if request.method == 'POST':
                file_type = str(request.FILES['image'].content_type[:6])
                if file_type != 'image/':
                    return JsonResponse({"message": "이미지 파일이 아닙니다."}, status=400)

                image_type = str(request.FILES['image'].content_type[6:])
                if image_type not in ['jpg', 'jpeg', 'png']:
                    return JsonResponse({"message": "jpg, jpeg, png 파일만 업로드 가능합니다."}, status=400)

                key = makeRandomString(36) + '.' + image_type
                FileSystemStorage().save(key, request.FILES['image'])
                return JsonResponse({"id": key}, status=200)

        else:
            return JsonResponse({"message": "올바르지 않은 접근입니다."}, status=405)

    except Exception:
        return JsonResponse({"message": "알 수 없는 오류가 발생했습니다."}, status=500)