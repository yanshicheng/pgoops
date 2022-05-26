from common.serializers import StandardModelSerializer
from .models import UserProfile, Department


class UserProfileSerializer(StandardModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ("password",)

    def to_representation(self, instance):
        representation = super(UserProfileSerializer, self).to_representation(instance)
        role_list = instance.role.all()
        representation["roles"] = (
            [] if not role_list else [role.name for role in role_list]
        )
        representation["dep"] = (
            instance.department.name if instance.department else None
        )
        return representation


class DepartmentSerializer(StandardModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(DepartmentSerializer, self).to_representation(instance)
        user_list = instance.user.all()
        representation["user"] = (
            []
            if not user_list
            else [UserProfileSerializer(user).data for user in user_list]
        )
        return representation
