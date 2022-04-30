from rest_framework.exceptions import ValidationError

from common.serializers import StandardModelSerializer
from .models import ServiceTree
from .models import NodeLinkOperaPermission
from .models import NodeLinkClassify
from .models import NodeLinkAsset
from .models import NodeJoinTag


class ServiceTreeListSerializer(StandardModelSerializer):
    class Meta:
        model = ServiceTree
        fields = (
            "pk",
            "name",
            "name_cn",
            "parent",
            "created_at",
            "updated_at",
            "level",
            "abspath",
            "appkey",
        )

        extra_kwargs = {
            "level": {
                "read_only": True,
            },
            "abspath": {
                "read_only": True,
            },
            "appkey": {
                "read_only": True,
            },
        }

        """validators 中的字段不能和extra_kwargs同时使用"""
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=ServiceTree.objects.all(),
        #         fields=['name', 'level']
        #     )
        # ]

    # def validate_name(self, value):
    #     return value

    def create(self, validated_data):
        parent_instance = validated_data["parent"]
        name = validated_data["name"]
        # 同一节点下节点名称不能重复
        if ServiceTree.objects.filter(parent=parent_instance, name=name).exists():
            raise ValidationError(
                detail="<{}> already exists under <{}> node.".format(
                    name, parent_instance.name
                )
            )

        # # 要求服务名称不能重复，暂时先关闭
        # if ServiceTree.objects.filter(level=parent_instance.get_level(), name=name).exists():
        #     raise ValidationError(detail="{} already exists.".format(name))

        return super(ServiceTreeListSerializer, self).create(validated_data)


class NodeLinkOperaPermissionModelSerializer(StandardModelSerializer):
    class Meta:
        model = NodeLinkOperaPermission
        fields = "__all__"


# class NodeLinkServerSerializer(StandardModelSerializer):
#     class Meta:
#         model = NodeLinkServer
#         fields = "__all__"
#
#     def validate(self, attrs):
#         """如果 node 非level=4, 不允许关联节点 触发异常"""
#         # {"node":21,"cmdbs":[3]}
#         node = attrs['node']
#         if node.get_level() != 4:
#             raise ValidationError("Mount server only leaf node.")
#         return attrs


class NodeJoinTagSerializer(StandardModelSerializer):
    class Meta:
        model = NodeJoinTag
        fields = "__all__"


class NodeLinkClassifySerializer(StandardModelSerializer):
    class Meta:
        model = NodeLinkClassify
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(NodeLinkClassifySerializer, self).to_representation(
            instance
        )
        representation["node_name"] = instance.node.name
        representation["classify_name"] = instance.classify.name
        return representation


class NodeLinkAssetSerializer(StandardModelSerializer):
    class Meta:
        model = NodeLinkAsset
        fields = "__all__"

    # def to_representation(self, instance):
    #     representation = super(NodeLinkAssetSerializer, self).to_representation(instance)
    #     representation['node_name'] = instance.node.name
    #     representation['classify_name'] = instance.classify.name
    #     return representation
