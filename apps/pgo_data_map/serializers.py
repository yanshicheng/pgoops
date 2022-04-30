from rest_framework import serializers

from common.serializers import StandardModelSerializer
from .models import Classify, Fields, Asset, ClassifyBind, AssetBind, ChangeRecord


class ClassifySerializer(StandardModelSerializer):
    class Meta:
        model = Classify
        fields = "__all__"


class FieldsSerializer(StandardModelSerializer):
    fields = serializers.JSONField()

    def validate_phone(self, fields):
        return fields

    class Meta:
        model = Fields
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(FieldsSerializer, self).to_representation(instance)
        representation["parent_classify_name"] = instance.classify.pid.name
        return representation


class AssetSerializer(StandardModelSerializer):
    class Meta:
        model = Asset
        fields = "__all__"

    #
    # def to_representation(self, instance):
    #     representation = super(AssetSerializer, self).to_representation(instance)
    #     representation['parent_table_classify'] = instance.table_classify.pid.name
    #     representation['field'] = FieldsSerializer(instance.table_classify.fields).data['fields']
    #     return representation
    #
    # def get_asset_children(self, instance):
    #     children_dic = {}
    #     table_relation_all = OperateInstance.get_parent_table_relation(instance.table_classify.id)
    #     if table_relation_all:
    #         for table_relation in table_relation_all:
    #             asset_relation_all = OperateInstance.get_parent_asset_relation(table_relation.id, instance.id)
    #             if asset_relation_all:
    #                 children_dic[table_relation.child_table.name] = []
    #
    #                 for asset_relation in asset_relation_all:
    #                     children_dic[table_relation.child_table.name].append(
    #                         AssetSerializer(asset_relation.child_asset).data)
    #     return children_dic


class ClassifyBindSerializer(StandardModelSerializer):
    class Meta:
        model = ClassifyBind
        fields = "__all__"


class AssetBindSerializer(StandardModelSerializer):
    class Meta:
        model = AssetBind
        fields = "__all__"


class ChangeRecordSerializer(StandardModelSerializer):
    class Meta:
        model = ChangeRecord
        fields = "__all__"
