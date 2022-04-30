from common.models import StandardModelMixin
from django.db import models

__all__ = [
    "Role",
    "Rule",
]


class Role(StandardModelMixin):
    """角色"""

    name = models.CharField(
        verbose_name="名称", help_text="名称", max_length=128, unique=True
    )
    rule = models.ManyToManyField(
        to="Rule", verbose_name="规则", blank=True, related_name="role"
    )

    def adapter(self):
        return [
            {
                "ptype": "g",
                "user": user.username,
                "role": self.name,
            }
            for user in self.user.all()
        ]

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_permission_role"
        unique_together = ("name",)
        verbose_name = verbose_name_plural = "角色"


# class RuleClassify(StandardModelMixin):
#     """ 权限分类 """
#     pass
# name = models.CharField(verbose_name='名称', help_text='分类名', max_length=120, unique=True)
#
# class Meta:
#     db_table = 'prem_rule_classify'
#     unique_together = ('name',)
#     verbose_name = verbose_name_plural = '角色'


class Rule(StandardModelMixin):
    """API权限"""

    name = models.CharField(verbose_name="名称", help_text="名称", max_length=64)
    path = models.CharField(max_length=128, verbose_name="api路径", blank=True, null=True)
    method = models.CharField(
        max_length=128, verbose_name="请求方法", blank=True, null=True
    )
    pid = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def adapter(self):
        return [
            {
                "ptype": "p",
                "role": role.name,
                "path": self.path,
                "method": self.method,
            }
            for role in self.role.all()
        ]

    class Meta:
        db_table = "pgo_permission_rules"
        verbose_name_plural = verbose_name = "权限规则"


class Menu(StandardModelMixin):
    order = models.IntegerField(verbose_name="子菜单排序")
    path = models.CharField(verbose_name="路由路径", max_length=64)
    component = models.CharField(
        verbose_name="视图路径", max_length=128, blank=True, null=True
    )
    name = models.CharField(verbose_name="路由名", max_length=32, blank=True, null=True)
    title = models.CharField(verbose_name="名称", max_length=32, blank=True, null=True)
    icon = models.CharField(verbose_name="图标名", max_length=32, blank=True, null=True)
    redirect = models.CharField(
        verbose_name="重定向", max_length=128, blank=True, null=True
    )
    active_menu = models.CharField(
        verbose_name="详情路由", max_length=128, blank=True, null=True
    )
    hidden = models.BooleanField(verbose_name="隐藏", default=False)
    always_show = models.BooleanField(verbose_name="显示根路由", default=True)
    no_cache = models.BooleanField(verbose_name="不缓存", default=False)
    breadcrumb = models.BooleanField(verbose_name="是否在面包屑显示", default=False)
    affix = models.BooleanField(verbose_name="固定", default=False)
    role = models.ManyToManyField(
        to=Role,
        verbose_name="权限角色",
        blank=True,
    )
    pid = models.ForeignKey(
        "self", verbose_name="父节点", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_permission_menu"
        verbose_name_plural = verbose_name = "前端菜单"
