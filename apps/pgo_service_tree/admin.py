from .models import ServiceTree
from .models import NodeJoinTag
from .models import NodeLinkClassify
from .models import NodeLinkAsset
from .models import NodeLinkOperaPermission

from django.contrib import admin
from mptt.admin import MPTTModelAdmin


# Register your models here.


@admin.register(ServiceTree)
class ServiceTreeAdmin(admin.ModelAdmin):
    readonly_fields = ("appkey", "abspath")


@admin.register(NodeLinkOperaPermission)
class NodeOwnerAdmin(admin.ModelAdmin):
    list_display = (
        "node",
        "read_member_custom",
        "write_member_custom",
    )
    filter_horizontal = ("read_member", "write_member")

    def read_member_custom(self, obj):
        member = obj.read_member.all()
        return [m.username for m in member]

    def write_member_custom(self, obj):
        member = obj.write_member.all()
        return [m.username for m in member]

    read_member_custom.short_description = "读权限"
    write_member_custom.short_description = "写权限"


@admin.register(NodeLinkClassify)
class NodeLinkClassifyAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "node",
        "cmdbs_custom",
    )

    def cmdbs_custom(self, obj):
        return obj.classify.name

    cmdbs_custom.short_description = "cmdb类型"


@admin.register(NodeLinkAsset)
class NodeLinkAssetAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "node_link",
        "asset_custom",
    )

    def asset_custom(self, obj):
        return obj.asset.data

    asset_custom.short_description = "节点资产"


@admin.register(NodeJoinTag)
class NodeJoinTagAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "node",
        "key",
        "value",
    )
