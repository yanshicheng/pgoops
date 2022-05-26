from django.conf import settings
from apps.pgo_user.models import UserProfile


def get_user(request):
    if settings.DEBUG:
        try:
            return request.user
        except Exception:
            return None

    else:
        try:
            u_id = request.user.id
            return UserProfile.objects.filter(id=u_id).first()
        except Exception as e:
            raise Exception("无法获取用户地址，请先登录")


def get_user_name(request):
    if settings.DEBUG:
        if request.user:
            return request.user.name
        else:
            return "agent"
    else:
        if request.user:
            return request.user.name
        else:
            raise Exception("无法获取用户地址，请先登录")


def get_addr(request):
    if "HTTP_X_FORWARDED_FOR" in request.META:
        ip = request.META["HTTP_X_FORWARDED_FOR"]
    else:
        ip = request.META["REMOTE_ADDR"]
    return ip
