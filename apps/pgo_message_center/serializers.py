from common.serializers import StandardModelSerializer
from .models import Group, Provider, History, Level


class GroupSerializers(StandardModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"

    def to_representation(self, instance: Group):
        representation = super(GroupSerializers, self).to_representation(instance)
        representation["user_name"] = [u.name for u in instance.user.all()]

        return representation


class ProviderSerializers(StandardModelSerializer):
    class Meta:
        model = Provider
        fields = "__all__"

    def to_representation(self, instance: Provider):
        representation = super(ProviderSerializers, self).to_representation(instance)
        representation["method_name"] = instance.get_method_display()

        return representation


class LevelSerializers(StandardModelSerializer):
    class Meta:
        model = Level
        fields = "__all__"

    def to_representation(self, instance: Level):
        representation = super(LevelSerializers, self).to_representation(instance)
        representation["provider_name"] = instance.provider.name
        representation["group_name"] = instance.group.name

        return representation


class HistorySerializers(StandardModelSerializer):
    class Meta:
        model = History
        fields = "__all__"

    def to_representation(self, instance: History):
        representation = super(HistorySerializers, self).to_representation(instance)
        representation["type_name"] = instance.get_type_display()
        representation["level_name"] = instance.level.cname
        representation["status"] = instance.get_status_display()
        representation["user_name"] = instance.user.name if instance.user else None

        return representation
