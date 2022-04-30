from django.contrib import admin

# Register your models here.
from . import models
from . import models


# for table in models.__all__:
#     admin.site.register(getattr(models, table))


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "rule_custom")
    search_fields = ["pk", "name"]

    def rule_custom(self, obj):
        return obj.adapter()

    rule_custom.short_description = "规则列表"


@admin.register(models.Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "path", "method", "pid_custom")
    search_fields = ["pk", "name", "path"]

    def pid_custom(self, obj):
        return obj.pid.name if obj.pid else None

    pid_custom.short_description = "父级标签"


@admin.register(models.Menu)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("pk", "path", "component", "name", "title")
    search_fields = ["pk", "title", "component", "path"]
