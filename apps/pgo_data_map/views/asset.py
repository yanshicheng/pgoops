import json
from rest_framework.decorators import action
from collections import OrderedDict
from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..models import Asset, AssetBind
from ..serializers import AssetSerializer

# from ..verify.check_data import check_data
from ..verify.check_data import check_data
from ..verify.operate import OperateInstance
from ..verify.record_log import record


class AssetViewSet(StandardModelViewSet):
    queryset = Asset.objects.filter().order_by("id")
    serializer_class = AssetSerializer
    ordering_fields = ("id",)
    filter_fields = ("id", "classify_id", "ban_bind")
    search_fields = ("data",)

    def list(self, request, *args, **kwargs):
        classify_id = request.query_params.get("classify_id")
        if not classify_id:
            return api_error_response("资产查询只能通过分类ID查询.")

        classify_obj = OperateInstance.get_classify(classify_id)

        if not classify_obj:
            return api_error_response("找不到指定的模型表")

        classify_field_obj = OperateInstance.get_classify_field(classify_id)
        if not classify_field_obj:
            return api_error_response("找不到分类表的字段表")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {
                    "data": serializer.data,
                    "fields": classify_field_obj.fields,
                    "rules": classify_field_obj.rules,
                    "patent_classify_name": classify_field_obj.classify.pid.name,
                    "classify_name": classify_field_obj.classify.name,
                    "classify_id": classify_field_obj.classify.id,
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        data = {
            "data": serializer.data,
            "fields": classify_field_obj.fields,
            "rules": classify_field_obj.rules,
            "patent_classify_name": classify_field_obj.classify.pid.name,
            "classify_name": classify_field_obj.classify.name,
            "classify_id": classify_field_obj.classify.id,
        }
        return api_ok_response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        classify_field_obj = OperateInstance.get_classify_field(instance.classify.id)
        data = OrderedDict()
        data["classify_name"] = instance.classify.name
        data["classify_id"] = instance.classify.id
        data["patent_classify_name "] = instance.classify.pid.name
        data["fields"] = classify_field_obj.fields
        data["rules"] = classify_field_obj.rules
        data["data"] = serializer.data
        data["children"] = OperateInstance.get_p_bind_asset(
            instance.id, instance.classify.id
        )
        data["relevant"] = OperateInstance.get_c_bind_asset(
            instance.id, instance.classify.id
        )
        return api_ok_response(data)

    def create(self, request, *args, **kwargs):
        # 校验数据
        try:
            data = check_data(request.data, None)
        except Exception as e:
            return api_error_response(f"数据校验出错: {str(e)}")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.get_success_headers(serializer.data)
        return api_ok_response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            data = check_data(request.data, instance)
        except ValueError as e:
            return api_error_response(f"数据校验出错: {str(e)}")

        if data.get("classify_id") and data.get("classify_id") != instance.classify.id:
            return api_error_response("数据不可修改类型, 如需更换请进行删除.")

        try:
            record("update_data", None, instance, request)
        except Exception as e:
            return api_error_response(f"日志记录出错: {str(e)}")

        partial = kwargs.pop("partial", False)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return api_ok_response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        try:
            record("delete_data", instance, None, request)
        except Exception as e:
            return api_error_response(f"日志记录出错: {str(e)}")

        instance.delete()
        return api_ok_response("删除成功")

    @action(methods=["post"], detail=False)
    def bind(self, request, *args, **kwargs):
        parent_asset_id = request.data.get("parent_asset_id")
        child_asset_id = request.data.get("child_asset_id")

        if not parent_asset_id or not child_asset_id:
            return api_error_response("parent_asset_id and child_asset_id 是必传参数")

        parent_asset_obj = OperateInstance.get_asset(parent_asset_id)
        child_asset_obj = OperateInstance.get_asset(child_asset_id)

        # 判断对应资产是否存在
        if not parent_asset_obj or not child_asset_obj:
            return api_error_response("找不到指定ID的资产")

        classify_bind_obj = OperateInstance.get_classify_bind(
            parent_asset_obj.classify.id, child_asset_obj.classify.id
        )

        # 判断分类关系绑定表是否存在
        if not classify_bind_obj:
            return api_error_response("未查询到分类关系绑定表, 请先进行绑定在进行资产绑定操作.")

        # 判断是否为 OneToOne 如果是则判断是否存在绑定记录
        bind_mode = classify_bind_obj.bind_mode
        if not bind_mode:
            asset_bind_obj = OperateInstance.get_child_asset_bind(
                classify_bind_obj.id, child_asset_obj.id
            )

            if asset_bind_obj:
                return api_error_response("类型表关联模式为: OneToOne, 子资产数据已经被绑定无法进行二次绑定.")

        try:
            new_asset_bind = AssetBind.objects.create(
                parent_asset=parent_asset_obj,
                child_asset=child_asset_obj,
                classify_bind=classify_bind_obj,
            )
            new_asset_bind.save()

        except Exception as e:
            return api_error_response(f"数据创建出错: {str(e)}")

        # 如果 OneToOne 设置子资产 禁止绑定
        if not bind_mode:
            child_asset_obj.ban_bind = True
            child_asset_obj.save()

        try:
            record("bind", parent_asset_obj, child_asset_obj, request)
        except Exception as e:
            return api_error_response(f"日志记录出错: {str(e)}")
        return api_ok_response("资产数据绑定成功")

    @action(methods=["delete"], detail=False, url_path="un-bind")
    def un_bind(self, request, *args, **kwargs):
        parent_asset_id = request.data.get("parent_asset_id")
        child_asset_id = request.data.get("child_asset_id")
        if not parent_asset_id or not child_asset_id:
            return api_error_response("parent_asset_id and child_asset_id 是必传参数")

        asset_bind_obj = OperateInstance.get_abs_asset_bind(
            parent_asset_id, child_asset_id
        )

        if not asset_bind_obj:
            return api_error_response("未查询到资产绑定记录, 请检查后重试.")

        try:
            record(
                "un_bind",
                asset_bind_obj.parent_asset,
                asset_bind_obj.child_asset,
                request,
            )
        except Exception as e:
            return api_error_response(f"日志记录出错: {str(e)}")

        if not asset_bind_obj.classify_bind.bind_mode:
            asset_bind_obj.child_asset.ban_bind = False
            asset_bind_obj.child_asset.save()

        asset_bind_obj.delete()
        return api_ok_response()

    @action(methods=["get"], detail=False)
    def search(self, request, *args, **kwargs):
        search_info = request.query_params.get("search")
        if not search_info:
            return api_error_response("必须输入查询内容才可进行查询搜索.")
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        data = []
        for item in json.loads(json.dumps(serializer.data)):

            for i, dic in enumerate(data):
                if item["classify"] in dic.values():
                    item["data"]["id"] = item["id"]
                    data[i]["data"].append(item["data"])
                    break
            else:
                tmp = {}
                classify = OperateInstance.get_classify(item["classify"])
                tmp["classify_id"] = classify.id
                tmp["classify_name"] = classify.name
                tmp["patent_classify_name"] = classify.pid.name
                tmp["fields"] = classify.fields.fields
                item["data"]["id"] = item["id"]
                tmp["data"] = [item["data"]]
                data.append(tmp)
        return api_ok_response(data)
