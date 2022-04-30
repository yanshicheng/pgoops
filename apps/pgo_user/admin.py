from django.contrib import admin
from mptt.admin import MPTTModelAdmin

# Register your models here.
from . import models

# for table in models.__all__:
#     admin.site.register(getattr(models,table))


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "name", "email", "phone", "role_custom")
    search_fields = ["pk", "name", "username", "email", "email"]

    # filter_horizontal = ('read_member', "write_member")

    def role_custom(self, obj):
        member = obj.role.all()
        return [m.name for m in member]

    role_custom.short_description = "角色"


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
    )
    search_fields = ["pk", "name"]
