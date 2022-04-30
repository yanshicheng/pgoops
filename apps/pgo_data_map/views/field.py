from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..models import Fields
from ..serializers import FieldsSerializer
from ..verify.check_filed import check_field
from ..verify.operate import OperateInstance


class FieldsViewSet(StandardModelViewSet):
    queryset = Fields.objects.filter().order_by("id")
    serializer_class = FieldsSerializer
    ordering_fields = ("id",)
    filter_fields = ("id",)
    search_fields = ("id",)

    def create(self, request, *args, **kwargs):
        classify_obj = OperateInstance.get_classify(request.data["classify"])

        # 判断 classify实例是否存在并且不是主分类
        if not classify_obj or not classify_obj.pid:
            return api_error_response(
                "classify_obj实例不存在或者classify_obj实例为主分类,主分类不允许创建字段表."
            )
        try:
            check_field(request.data)
        except Exception as e:
            return api_error_response(f"数据校验出错: {str(e)}")
        return super(FieldsViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        # 判断如果更换 classify_id 当前 instance 是否存在资产
        if instance.classify.id != data["classify"] and OperateInstance.get_all_asset(
            instance.classify.id
        ):
            return api_error_response("分类表已经存在资产, 字段表不允许更换主类.")

        # 判断更换的 classify 是否是 主分类表
        if not OperateInstance.get_classify(data["classify"]).pid:
            return api_error_response("指定的分类表为主分类,主分类无法设置表字段.")

        # 检查数据
        try:
            check_field(data)
        except Exception as e:
            return api_error_response(f"数据校验出错: {str(e)}")

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return api_ok_response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if OperateInstance.get_all_asset(instance.classify.id):
            return api_error_response("删除字段存在数据无法进行删除操作")
        instance.delete()
        return api_ok_response()
