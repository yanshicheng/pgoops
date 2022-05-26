from rest_framework.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_403_FORBIDDEN,
)
from rest_framework.response import Response, SimpleTemplateResponse


def api_response(code, data, message, status=HTTP_200_OK):
    data = {"code": code, "data": data, "message": message}
    return Response(data, status=status)


def api_ok_response(data="success"):
    return api_response(code=0, data=data, message=None)


def api_error_response(message="error", status=HTTP_200_OK):
    return api_response(code=-1, data=None, message=message, status=status)
