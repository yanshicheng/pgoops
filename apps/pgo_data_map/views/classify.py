import json

from rest_framework.decorators import action
from django.core.files.uploadedfile import InMemoryUploadedFile

from ..models import Classify, ClassifyBind
from ..serializers import ClassifySerializer
from ..verify.operate import OperateInstance
from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response


class ClassifyViewSet(StandardModelViewSet):
    queryset = Classify.objects.filter().order_by("id")
    serializer_class = ClassifySerializer
    ordering_fields = ("id", "name", "pid")
    filter_fields = ("id", "name", "pid", "ban_bind")
    search_fields = ("name",)

    def create(self, request, *args, **kwargs):
        data = request.data
        pid = data.get("pid")
        # 如果新建数据存在PID
        if pid:
            # 查询 id = pid 的实例, 如果实例的PID不为Null则返回错误
            if OperateInstance.get_classify(pid).pid:
                return api_error_response(f"指定的pid:({pid}) 不是主分类表.")
        return super(ClassifyViewSet, self).create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = json.loads(json.dumps(request.data))
        pid = data.get("pid")
        # 判断是否存在PID
        if pid:
            # 查询 pid = instance.id 的表, 如果存在则报错.
            if OperateInstance.get_children_classify(instance.id):
                return api_error_response("无法修改, 此类型表存在子分类表.")
            # 获取要指定为主类的实例, 并判断是否为主类 也就是 PID == Null
            parent_classify = OperateInstance.get_classify(pid)
            if not parent_classify or parent_classify.pid:
                return api_error_response("指定的 pid 不存在或者不是主分类表.")
        if data.get("icon"):
            if not isinstance(data.get("icon"), InMemoryUploadedFile):
                del data["icon"]
        serializer = self.get_serializer(
            instance, data=data, partial=kwargs.pop("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer, request)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return api_ok_response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 如果没有 pid 则为主分类表
        if not instance.pid:
            child_classify_all = OperateInstance.get_children_classify(instance.id)
            if child_classify_all:
                return api_error_response("如果删除主类型请先删除实体模型表.")

        # 清理关联表
        classify_relation = OperateInstance.get_parent_classify_bind(instance.id)
        if classify_relation:
            for inc in classify_relation:
                if inc.child_classify.ban_bind:
                    inc.delete()

        instance.delete()
        return api_ok_response("删除成功")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        field_obj = OperateInstance.get_classify_field(instance.id)
        if field_obj:
            data["rules"] = field_obj.rules
            data["field_id"] = field_obj.id
            data["fields"] = field_obj.fields
        else:
            data["field_id"] = None
            data["rules"] = None
            data["fields"] = None
        children_all = OperateInstance.get_parent_classify_bind(instance.id)
        data["children"] = []
        data["relevant"] = []
        if children_all:
            for item in children_all:
                dic = self.get_serializer(item.child_classify).data
                dic["parent_name"] = item.child_classify.pid.name
                dic["bind_mode"] = item.bind_mode
                data["children"].append(dic)
        relevant_all = OperateInstance.get_child_classify_bind(instance.id)
        if relevant_all:
            for item in relevant_all:
                dic = self.get_serializer(item.parent_classify).data
                dic["parent_name"] = item.parent_classify.pid.name
                dic["bind_mode"] = item.bind_mode
                data["relevant"].append(dic)

        return api_ok_response(data)

    @action(methods=["get"], detail=False)
    def tree(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = []
        for item in json.loads(json.dumps(serializer.data)):
            if not item["pid"]:
                for dic in data:
                    if dic["id"] == item["id"]:
                        break
                else:
                    item["children"] = []
                    data.append(item)
            else:
                for i, dic in enumerate(data):
                    if dic["id"] == item["pid"]:
                        data[i]["children"].append(item)
                        break
                else:
                    parent_data = self.get_serializer(
                        OperateInstance.get_classify(item["pid"])
                    )
                    tmp_data = json.loads(json.dumps(parent_data.data))
                    tmp_data["children"] = []
                    tmp_data["children"].append(item)
                    data.append(tmp_data)
        return api_ok_response(data)

    @action(methods=["post"], detail=False)
    def bind(self, request, *args, **kwargs):
        data = request.data
        parent_classify_id = data.get("parent_classify_id")
        child_classify_id = data["child_classify_id"]

        if not parent_classify_id or not child_classify_id:
            return api_error_response("parent_classify_id and child_classify_id 是必传参数.")

        parent_classify = OperateInstance.get_classify(parent_classify_id)
        child_classify = OperateInstance.get_classify(child_classify_id)

        # 验证表是否存在
        if not parent_classify or not child_classify:
            return api_error_response("parent分类表或者child分类表不存在")

        # 验证 是否有
        if not parent_classify.pid or not child_classify.pid:
            return api_error_response("parent分类表或者child分类表是主分类表, 不允许进行绑定操作.")
        # 验证 child 和 parent 是否为同一个表
        if parent_classify.id == child_classify.id:
            return api_error_response("不支持自关联.")

        # 验证 是否禁止绑定.
        if child_classify.ban_bind:
            return api_error_response("child表,禁止绑定操作.")

        # 验证是否存在字段表
        parent_field = OperateInstance.get_classify_field(parent_classify_id)
        child_field = OperateInstance.get_classify_field(child_classify_id)
        if not parent_field or not child_field:
            return api_error_response("parent类型表或者child类型表没有字段表")

        classify_relation_obj = ClassifyBind.objects.create(
            parent_classify_id=parent_classify_id,
            child_classify_id=child_classify_id,
            bind_mode=data.get("bind_mode"),
        )

        if request.data.get("ban_bind"):
            child_classify.ban_bind = True
            child_classify.save()

        classify_relation_obj.save()
        return api_ok_response("关联成功")

    @action(methods=["delete"], detail=False, url_path="un-bind")
    def un_bind(self, request, *args, **kwargs):
        data = request.data
        parent_classify_id = data["parent_classify_id"]
        child_classify_id = data["child_classify_id"]

        if not parent_classify_id or not child_classify_id:
            return api_error_response("parent_classify_id and child_classify_id 是必传参数.")

        classify_relation_obj = OperateInstance.get_classify_bind(
            parent_classify_id, child_classify_id
        )
        if not classify_relation_obj:
            return api_error_response(
                f"找不到parent_classify_id为:{parent_classify_id}, child_classify_id为: {child_classify_id} 关系记录"
            )

        # 修改 child_classify_obj 的值
        child_classify_obj = OperateInstance.get_classify(child_classify_id)
        if child_classify_obj.ban_bind:
            child_classify_obj.ban_bind = False
            child_classify_obj.save()

        classify_relation_obj.delete()
        return api_ok_response("解除关联成功")

    @action(methods=["get"], detail=False)
    def parent(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(pid=None)
        serializer = self.get_serializer(queryset, many=True)
        return api_ok_response(serializer.data)
