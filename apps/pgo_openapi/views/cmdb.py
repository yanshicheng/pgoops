from apps.pgo_openapi.lib.cmdb_lib import cmdb
from common.encrypt import decrypt_base64_aes
from common.views import StandardOpenApiView
from common.response import api_ok_response, api_error_response


class CmdbOpenApiView(StandardOpenApiView):
    """
    通过token用户信息
    """

    def post(self, request, *args, **kwargs):
        # 解密数据
        data = request.data.get('data')
        # data, ok = decrypt_base64_aes(request.data.get('data'))
        # if not ok:
        #     return api_error_response(data)
        children_data = data.pop("children")
        if len(data) != 1:
            return api_error_response("数据格式错误!")
        parent_obj = cmdb("parent_classify", data, None)
        parent_obj = cmdb("children_classify", children_data, parent_obj)
        return api_ok_response()
