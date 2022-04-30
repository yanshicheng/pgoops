from common.response import api_error_response, api_ok_response
from common.viewsets import StandardModelViewSet

from ..models import NodeLinkClassify, NodeLinkAsset
from ..serializers import NodeLinkClassifySerializer
from ...pgo_data_map.verify.operate import OperateInstance


class NodeLinkClassifyViewSet(StandardModelViewSet):
    queryset = NodeLinkClassify.objects.filter().order_by("-id")
    serializer_class = NodeLinkClassifySerializer
    ordering_fields = ("id",)
    filter_fields = ("id", "node_id")
    search_fields = ()

    def create(self, request, *args, **kwargs):
        data = request.data
        cid = data.get("classify")
        # 如果新建数据存在PID
        if cid:
            # 查询 id = pid 的实例, 如果实例的PID不为Null则返回错误
            if OperateInstance.get_classify(cid).ban_bind:
                return api_error_response(f"指定的 classify 类型表禁止绑定.")
        return super(NodeLinkClassifyViewSet, self).create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        na = NodeLinkAsset.objects.filter(node_link=instance.id)
        if na:
            return api_error_response("类型下已经绑定数据, 请先清空数据后重试!")
        instance.delete()
        return api_ok_response()
