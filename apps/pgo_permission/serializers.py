from common.serializers import StandardModelSerializer
from .models import Role, Rule, Menu


class RoleSerializer(StandardModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RuleSerializer(StandardModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"


class MenuSerializer(StandardModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(MenuSerializer, self).to_representation(instance)
        role_list = instance.role.all()
        representation["roles"] = (
            [] if not role_list else [role.name for role in role_list]
        )
        return representation
