from common.models import StandardModelMixin
from apps.pgo_user.models import UserProfile
from apps.pgo_data_map.models import Classify, Asset
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

MAX_LEVEL = 5


# Create your models here.
class ServiceTree(MPTTModel, StandardModelMixin):
    """
    服务树核心表
        公司
            部门
                项目
                    服务
                        环境
    """

    name = models.CharField(max_length=100, db_index=True, verbose_name="节点名称-英文")
    name_cn = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="节点名称-中文"
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="父级",
    )
    abspath = models.CharField(
        max_length=200, db_index=True, null=False, blank=False, verbose_name="abspath"
    )
    appkey = models.CharField(
        max_length=200, db_index=True, null=False, blank=False, verbose_name="appkey"
    )

    def __str__(self):
        return "{} | {} | {}".format(self.pk, self.name, self.name_cn)

    class MPTTMeta:
        order_insertion_by = ["name"]

    class Meta:
        db_table = "pgo_service_tree"
        verbose_name = "服务树基础表"
        verbose_name_plural = verbose_name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.name = self.name.lower()
        if self.parent:

            # 1. 限制 最多的层级5 索引为4
            if self.parent.level == MAX_LEVEL - 1:
                raise ValueError("level crossing.")

            """
            abspath = all_parent_abspath + name
            appkey = parent_appkey + name
            """
            # 2. 自动生成 abspath 节点
            nodes = [
                p.name.lower() for p in self.parent.get_ancestors(include_self=True)
            ]
            nodes.append(self.name)
            self.abspath = ".".join(nodes)

            # 3. 自动生成 appkey 字段
            self.appkey = ".".join([self.parent.appkey, self.name])
        else:
            self.abspath = self.name
            self.appkey = ".".join(["com", self.name])

        return super(ServiceTree, self).save(
            force_insert=False, force_update=False, using=None, update_fields=None
        )


class NodeLinkOperaPermission(StandardModelMixin):
    """
    节点操作权限权限
        - read
        - write
    """

    read_member = models.ManyToManyField(
        to=UserProfile, related_name="read_member", blank=True, verbose_name="read 成员"
    )
    write_member = models.ManyToManyField(
        to=UserProfile, related_name="write_member", blank=True, verbose_name="write 成员"
    )
    # node = models.ForeignKey(to=ServiceTree, on_delete=models.CASCADE, verbose_name='节点')
    node = models.OneToOneField(
        to=ServiceTree, on_delete=models.CASCADE, verbose_name="节点"
    )

    class Meta:
        db_table = "pgo_service_tree_node_permission"
        verbose_name = "节点操作权限"
        verbose_name_plural = verbose_name


class NodeLinkClassify(StandardModelMixin):
    """
    节点下关联CMDB类型
    """

    node = models.ForeignKey(
        to=ServiceTree, on_delete=models.CASCADE, verbose_name="节点"
    )
    classify = models.ForeignKey(
        to=Classify,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="link_classify",
    )

    class Meta:
        db_table = "pgo_service_tree_node_classify"
        unique_together = ("node", "classify")
        verbose_name = "节点关联CMDB类型"
        verbose_name_plural = verbose_name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.node:
            if self.node.level != 4:
                raise ValueError("当前节点禁止操作!")
        return super(NodeLinkClassify, self).save(
            force_insert=False, force_update=False, using=None, update_fields=None
        )


class NodeLinkAsset(StandardModelMixin):
    """
    节点下关联CMDB资产
    """

    node_link = models.ForeignKey(
        to=ServiceTree, on_delete=models.CASCADE, verbose_name="关联表"
    )
    asset = models.ForeignKey(
        to=Asset, blank=True, on_delete=models.CASCADE, related_name="link_asset"
    )

    class Meta:
        db_table = "pgo_service_tree_node_asset"
        unique_together = ("node_link", "asset")
        verbose_name = "节点关联CMDB资产"
        verbose_name_plural = verbose_name


class NodeJoinTag(StandardModelMixin):
    """
    节点关联标签
        node 和 key 唯一索引
    """

    node = models.ForeignKey(
        to=ServiceTree, on_delete=models.CASCADE, verbose_name="节点"
    )
    key = models.CharField(max_length=32, db_index=True, verbose_name="Key")
    value = models.JSONField(blank=False, null=False, verbose_name="Value")

    class Meta:
        db_table = "pgo_service_tree_node_tag"
        verbose_name = "节点关联Tag"
        verbose_name_plural = verbose_name
