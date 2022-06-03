from django.contrib import auth
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.decorators import action

from common.jwt_auth import MyTokenSerializer
from common.viewsets import StandardModelViewSet
from common.views import StandardOpenApiView, StandardApiView
from common.response import api_ok_response, api_error_response
from ..models import UserProfile
from ..serializers import UserProfileSerializer


class UserProfileViewSet(StandardModelViewSet):
    queryset = UserProfile.objects.filter().order_by("-id")
    serializer_class = UserProfileSerializer

    ordering_fields = ("id",)
    filter_fields = ("id",)
    search_fields = ("name",)

    def create(self, request, *args, **kwargs):
        try:
            serializer = UserProfileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_obj = serializer.save()
            user_obj.set_password(request.data.get("password"))
            user_obj.save()
            return api_ok_response(data=serializer.data)
        except Exception as e:
            return api_error_response(message=str(e))

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        if data.get("icon"):
            if not isinstance(data.get("icon"), InMemoryUploadedFile):
                del data["icon"]
        else:
            del data["icon"]
        serializer = self.get_serializer(
            instance, data=data, partial=kwargs.pop("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return api_ok_response(serializer.data)

    @action(methods=["put"], detail=True, url_path="change-password")
    def change_password(self, request, pk):
        """
        普通用户 修改密码
        """
        username = request.data.get("username")
        old_pwd = request.data.get("old_password")
        new_pwd = request.data.get("new_password")
        if username and old_pwd and new_pwd:
            user_obj = auth.authenticate(request, username=username, password=old_pwd)
            if user_obj:
                user_obj.set_password(new_pwd.strip())
                user_obj.save()
                return api_ok_response(data=f"{user_obj.username} 账户密码修改成功!")
            else:
                return api_error_response(message="用户或密码错误,请检查重试!")
        else:
            return api_error_response(
                message="<username>,<old_password>,<new_password>为必传参数."
            )

    @action(methods=["put"], detail=True, url_path="reset-password")
    def reset_password(self, request, pk):
        """管理员重置密码"""
        instance = self.get_object()
        new_pwd = request.data.get("new_password")
        if new_pwd:
            instance.set_password(new_pwd.strip())
            instance.save()

            return api_ok_response(data=f"{instance.name} 账户密码修改成功!")
        else:
            return api_error_response(message="<name>,<new_password>为必传参数.")

    def list(self, request, *args, **kwargs):
        return super(UserProfileViewSet, self).list(request, *args, **kwargs)


class UserInfoApiView(StandardApiView):
    """
    通过token用户信息
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            u = UserProfile.objects.get(id=user.id)
        except UserProfile.DoesNotExist:
            return api_error_response(message="not found")
        s = UserProfileSerializer(u)
        return api_ok_response(data=s.data)


class UserLogoutApiView(StandardOpenApiView):
    """
    通过token用户信息
    """

    def post(self, request, *args, **kwargs):
        return api_ok_response(data="ok")

from rest_framework_simplejwt.views import TokenViewBase
# 自定义的登陆视图
class UserLogIntApiView(TokenViewBase):
    serializer_class = MyTokenSerializer  # 使用刚刚编写的序列化类
    authentication_classes = []
    permission_classes = []

    # post方法对应post请求，登陆时post请求在这里处理
    def post(self, request, *args, **kwargs):
        # 使用刚刚编写时序列化处理登陆验证及数据响应
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return api_error_response(str(e))

        return api_ok_response(serializer.validated_data)
