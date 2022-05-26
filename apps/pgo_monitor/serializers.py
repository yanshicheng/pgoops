import os.path

from rest_framework import serializers

from .models import Rules, Group, Application, Node
from common.serializers import StandardModelSerializer


class NodeModelMixinSerializer(StandardModelSerializer):
    class Meta:
        model = Node
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(NodeModelMixinSerializer, self).to_representation(
            instance
        )
        representation["scheme_name"] = instance.get_scheme_display()
        representation["host_name"] = instance.host.get_unique_data()
        return representation

    def validate(self, attrs):
        config_path: str = attrs.get("config_path")
        rules_path: str = attrs.get("rules_path")
        if not config_path.strip().startswith("/"):
            raise serializers.ValidationError("prometheus 配置文件路径必须是绝对路径")
        if config_path.strip().endswith(".yml") or config_path.strip().endswith(
            ".yaml"
        ):
            attrs["config_path"] = config_path.strip()
        else:
            attrs["config_path"] = os.path.join(config_path, "prometheus.yml")
        if rules_path.strip().endswith(".yml") or rules_path.strip().endswith(".yaml"):
            attrs["rules_path"] = rules_path.strip()
        else:
            attrs["rules_path"] = os.path.join(rules_path, "rules.yml")
        return attrs


class GroupModelMixinSerializer(StandardModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

    def to_representation(self, instance: Group):
        representation = super(GroupModelMixinSerializer, self).to_representation(
            instance
        )
        representation["scheme_name"] = instance.get_scheme_display()
        return representation


class ApplicationModelMixinSerializer(StandardModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"

    def to_representation(self, instance: Application):
        representation = super(ApplicationModelMixinSerializer, self).to_representation(
            instance
        )
        representation["scheme_name"] = instance.get_scheme_display()
        representation["group_name"] = instance.group.name
        representation["asset_name"] = instance.asset.get_unique_data()
        return representation


class RulesModelMixinSerializer(StandardModelSerializer):
    class Meta:
        model = Rules
        fields = "__all__"

    def to_representation(self, instance: Rules):
        representation = super(RulesModelMixinSerializer, self).to_representation(
            instance
        )
        representation["group_name"] = instance.group.name
        representation["condition_name"] = instance.get_condition_display()
        representation["severity_name"] = (
            instance.severity.name if instance.severity else None
        )
        return representation

    def validate(self, attrs):
        duration = attrs.get("duration")
        if duration.endswith("s") or duration.endswith("m") or duration.endswith("h"):
            return attrs
        raise serializers.ValidationError("持续时间必须以 s,m,h 为结尾单位")
