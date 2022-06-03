from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, authentication, status
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

if not isinstance(api_settings.AUTH_HEADER_TYPES, (list, tuple)):
    AUTH_HEADER_TYPES = (AUTH_HEADER_TYPES,)

AUTH_HEADER_TYPE_BYTES = {h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES}

from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import serializers

from django.contrib.auth import get_user_model


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, ldap=None, **kwargs):
        ldap = request.data.get('ldap')
        try:
            # 小编这里添加了一个手机验证，如果需要其他验证再加就ok了
            if not ldap:
                try:
                    user = get_user_model().objects.get(Q(username=username) | Q(email=username))
                except Exception as e:
                    raise ValueError(f'用户或密码错误: {username}')

                if user.check_password(password):
                    return user
                else:
                    # 如果不想密码登录也可以验证码在这里写
                    # 这里做验证码的操作
                    raise serializers.ValidationError(f'用户或密码错误: {username}')
            else:
                # ldap 方式登陆
                pass

        except Exception as e:
            raise e


class InvalidToken(AuthenticationFailed):
    status_code = status.HTTP_200_OK
    default_detail = _("Token is invalid or expired")
    default_code = "token_not_valid"


class JWTAuthentication(authentication.BaseAuthentication):
    """
    An authentication plugin that authenticates requests through a JSON web
    token provided in a request header.
    """

    www_authenticate_realm = "api"
    media_type = "application/json"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_model = get_user_model()

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            raise InvalidToken(
                {
                    "data": {},
                    "message": "身份验证未提供，请登陆后重试",
                    "code": 10401,
                    "detail": "身份验证未提供"
                }
            )
        raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def authenticate_header(self, request):
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def get_header(self, request):
        """
        Extracts the header containing the JSON web token from the given
        request.
        """
        header = request.META.get(api_settings.AUTH_HEADER_NAME)

        if isinstance(header, str):
            # Work around django test client oddness
            header = header.encode(HTTP_HEADER_ENCODING)

        return header

    def get_raw_token(self, header):
        """
        Extracts an unvalidated JSON web token from the given "Authorization"
        header value.
        """
        parts = header.split()
        if len(parts) == 0:
            raise InvalidToken(
                {
                    "data": {},
                    "message": "身份验证未提供，请登陆后重试",
                    "code": 10401,
                    "detail": "身份验证未提供"
                }
            )
        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            raise InvalidToken(
                {
                    "data": {},
                    "message": "提供token格式错误",
                    "code": 10401,
                    "detail": "token 错误"
                }
            )
        if len(parts) != 2:
            raise InvalidToken(
                {
                    "data": {},
                    "message": "授权头必须包含两个空格分隔的值",
                    "code": 10401,
                    "detail": "token 错误"
                }
            )

        return parts[1]

    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        message = ""
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                message = e.args[0]

        raise InvalidToken(
            {
                "data": {},
                "message": message,
                "code": 10402,
            }
        )

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("12 Token contained no recognizable user identification"))

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed(_("13 User not found"), code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed(_("14 User is inactive"), code="user_inactive")

        return user


# 重写TokenObtainPairSerializer类的部分方法以实现自定义数据响应结构和payload内容
class MyTokenSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        """
        此方法往token的有效负载 payload 里面添加数据
        例如自定义了用户表结构，可以在这里面添加用户邮箱，头像图片地址，性别，年龄等可以公开的信息
        这部分放在token里面是可以被解析的，所以不要放比较私密的信息

        :param user: 用戶信息
        :return: token
        """
        token = super().get_token(user)
        # 添加个人信息
        token['name'] = user.username
        return token

    def validate(self, attrs):
        """
        此方法为响应数据结构处理
        原有的响应数据结构无法满足需求，在这里重写结构如下：
        {
            "refresh": "xxxx.xxxxx.xxxxx",
            "access": "xxxx.xxxx.xxxx",
            "expire": Token有效期截止时间,
            "username": "用户名",
            "email": "邮箱"
        }

        :param attrs: 請求參數
        :return: 响应数据
        """
        # data是个字典
        # 其结构为：{'refresh': '用于刷新token的令牌', 'access': '用于身份验证的Token值'}
        data = super().validate(attrs)

        # 获取Token对象
        refresh = self.get_token(self.user)
        # 令牌到期时间
        data['expire'] = refresh.access_token.payload['exp']  # 有效期
        # 用户名
        data['username'] = self.user.username
        # 邮箱
        data['email'] = self.user.email
        return data
