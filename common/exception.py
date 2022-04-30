from rest_framework.views import exception_handler
from common.response import api_ok_response, api_error_response

import logging

logger = logging.getLogger("drf_exception")


def custom_exception_handler(exc, context):
    """自定义异常"""
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, list):
            message = response.data[0]
        else:
            message = (
                response.data.get("detail")
                if response.data.get("detail")
                else response.data
            )
    else:
        message = f"异常信息： {exc}"
    logger.error(message)
    return api_error_response(message)
