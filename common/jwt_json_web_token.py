# from datetime import datetime
#
# from rest_framework import serializers
# from rest_framework.views import APIView
# from rest_framework.response import Response
#
# from django.utils.translation import ugettext as _
# from django.contrib.auth import authenticate, get_user_model
# from common.response import api_ok_response, api_error_response
# #
# from rest_framework_jwt.settings import api_settings
# from rest_framework_jwt import serializers as jwt_serializers
# from rest_framework_jwt.compat import get_username_field, PasswordField
# from rest_framework_jwt.compat import Serializer as compat_serializers
# #
# # User = get_user_model()
# jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
# jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
# jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#
#
# class JSONWebTokenAPIView(APIView):
#     """
#     重写 JsonWebTokenAPI 类
#     """
#
#     permission_classes = ()
#     authentication_classes = ()
#
#     def get_serializer_context(self):
#         """
#         Extra context provided to the serializer class.
#         """
#         return {
#             "request": self.request,
#             "view": self,
#         }
#
#     def get_serializer_class(self):
#         """
#         Return the class to use for the serializer.
#         Defaults to using `self.serializer_class`.
#         You may want to override this if you need to provide different
#         serializations depending on the incoming request.
#         (Eg. admins get full serialization, others get basic serialization)
#         """
#         assert self.serializer_class is not None, (
#                 "'%s' should either include a `serializer_class` attribute, "
#                 "or override the `get_serializer_class()` method." % self.__class__.__name__
#         )
#         return self.serializer_class
#
#     def get_serializer(self, *args, **kwargs):
#         """
#         Return the serializer instance that should be used for validating and
#         deserializing input, and for serializing output.
#         """
#         serializer_class = self.get_serializer_class()
#         kwargs["context"] = self.get_serializer_context()
#         return serializer_class(*args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#
#         if serializer.is_valid():
#             user = serializer.object.get("user") or request.user
#             token = serializer.object.get("token")
#             response_data = jwt_response_payload_handler(token, user, request)
#             response = Response(response_data)
#             if api_settings.JWT_AUTH_COOKIE:
#                 expiration = datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
#                 response.set_cookie(
#                     api_settings.JWT_AUTH_COOKIE,
#                     token,
#                     expires=expiration,
#                     httponly=True,
#                 )
#             return api_ok_response(response.data)
#
#         return api_error_response(serializer.errors)
#
#
# class JSONWebToken(compat_serializers):
#     """
#     重写登陆认证类
#     """
#
#     def __init__(self, *args, **kwargs):
#         """
#         Dynamically add the USERNAME_FIELD to self.fields.
#         """
#         super().__init__(*args, **kwargs)
#
#         self.fields[self.username_field] = serializers.CharField()
#         self.fields["password"] = PasswordField(write_only=True)
#
#     @property
#     def username_field(self):
#         return get_username_field()
#
#     def validate(self, attrs):
#         credentials = {
#             self.username_field: attrs.get(self.username_field),
#             "password": attrs.get("password"),
#         }
#         if all(credentials.values()):
#             user = authenticate(**credentials)
#
#             if user:
#                 if not user.is_active:
#                     msg = _("User account is disabled.")
#                     raise serializers.ValidationError(msg)
#
#                 payload = jwt_payload_handler(user)
#
#                 return {"token": jwt_encode_handler(payload), "user": user}
#             else:
#                 msg = _("用户名或密码错误")
#                 raise serializers.ValidationError(msg)
#         else:
#             msg = _('Must include "{username_field}" and "password".')
#             msg = msg.format(username_field=self.username_field)
#             raise serializers.ValidationError(msg)
#
#
# class ObtainJSONWebToken(JSONWebTokenAPIView):
#     """
#     API View that receives a POST with a user's username and password.
#
#     Returns a JSON Web Token that can be used for authenticated requests.
#     """
#
#     serializer_class = JSONWebToken
#
#
# class VerifyJSONWebToken(JSONWebTokenAPIView):
#     """
#     API View that checks the veracity of a token, returning the token if it
#     is valid.
#     """
#
#     serializer_class = jwt_serializers.VerifyJSONWebTokenSerializer
#
#
# class RefreshJSONWebToken(JSONWebTokenAPIView):
#     """
#     API View that returns a refreshed token (with new expiration) based on
#     existing token
#
#     If 'orig_iat' field (original issued-at-time) is found, will first check
#     if it's within expiration window, then copy it to the new token
#     """
#
#     serializer_class = jwt_serializers.RefreshJSONWebTokenSerializer
#
#
# obtain_jwt_token = ObtainJSONWebToken.as_view()
# refresh_jwt_token = RefreshJSONWebToken.as_view()
# verify_jwt_token = VerifyJSONWebToken.as_view()


def jwt_response_payload_handler(token, user=None, request=None):
    """
    设置jwt登陆返回的格式
    :param token:
    :param user:
    :param request:
    :return:
    """
    data = {"code": 0, "data": {'token': token}, "message": ""}

    return data
