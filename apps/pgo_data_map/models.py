from django.db import models

# Create your models here.
from common.models import StandardModelMixin
from common.authmodel import AuthorModelMixin

__all__ = [
    "Classify",
    "Fields",
    "Asset",
    "ClassifyBind",
    "AssetBind",
]


class Classify(StandardModelMixin, AuthorModelMixin):
    """分类表"""

    name = models.CharField(max_length=32, unique=True, verbose_name="名称")
    alias = models.CharField(
        max_length=32, unique=True, verbose_name="别名", null=True, blank=True
    )
    icon = models.ImageField(
        upload_to="data_map/icon/%Y/%m/%d/",
        default="data_map/icon/2021/08/19/pgoops.png",
        blank=True,
        null=True,
    )
    record_log = models.BooleanField(default=False, verbose_name="是否记录日志")
    ban_bind = models.BooleanField(default=False, verbose_name="是否允许绑定")
    pid = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="父Id"
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_data_map_classify"
        verbose_name = "表分类"
        verbose_name_plural = verbose_name

    def get_unique_fields(self):
        fields_dic = self.fields.fields
        for k, v in fields_dic.items():
            if v["guid"] == True:
                return k
        return None


class Fields(StandardModelMixin, AuthorModelMixin):
    """表字段 & 验证规则"""

    classify = models.OneToOneField(
        to=Classify,
        on_delete=models.CASCADE,
        verbose_name="关联Classify",
        related_name="fields",
    )
    fields = models.JSONField(
        default=dict,
        verbose_name="字段元数据",
    )
    rules = models.JSONField(default=dict, verbose_name="字段验证规则")

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "pgo_data_map_fields"
        verbose_name = "表字段"
        verbose_name_plural = verbose_name


class Asset(StandardModelMixin, AuthorModelMixin):
    """资产数据表"""

    classify = models.ForeignKey(
        to=Classify, on_delete=models.CASCADE, verbose_name="关联Classify"
    )
    data = models.JSONField(default=dict, verbose_name="数据值")
    ban_bind = models.BooleanField(default=False, verbose_name="禁止绑定")

    def __str__(self):
        return f"{self.pk}"

    class Meta:
        db_table = "pgo_data_map_asset"
        verbose_name = "表数据"
        verbose_name_plural = verbose_name

    def get_unique_data(self):
        try:
            unique_field = self.classify.get_unique_fields()
            return self.data[unique_field]
        except Exception:
            return None

    def get_service_tree_env(self):
        if hasattr(self, "link_asset") and self.link_asset:
            key_list = self.link_asset.node_link.node.appkey.split(".")
            return {"project": key_list[-2], "env": key_list[-1]}
        else:
            return {"project": "default", "env": "default"}


class ClassifyBind(StandardModelMixin):
    """分类绑定关系表"""

    parent_classify = models.ForeignKey(
        to=Classify,
        on_delete=models.CASCADE,
        related_name="parent",
        verbose_name="主表ID",
    )
    child_classify = models.ForeignKey(
        to=Classify,
        on_delete=models.CASCADE,
        related_name="child",
        verbose_name="子表ID",
    )
    bind_mode = models.BooleanField(default=True, verbose_name="是ForeignKey")

    class Meta:
        db_table = "pgo_data_map_classify_bind"
        unique_together = ("parent_classify", "child_classify")
        verbose_name = "表关联"
        verbose_name_plural = verbose_name


class AssetBind(StandardModelMixin):
    """资产绑定关系表"""

    parent_asset = models.ForeignKey(
        to=Asset,
        on_delete=models.CASCADE,
        related_name="parent",
        verbose_name="主记录ID",
    )
    child_asset = models.ForeignKey(
        to=Asset,
        on_delete=models.CASCADE,
        related_name="child",
        verbose_name="主记录ID",
    )
    classify_bind = models.ForeignKey(
        to=ClassifyBind, on_delete=models.CASCADE, verbose_name="表关系"
    )

    class Meta:
        db_table = "pgo_data_map_asset_bind"
        unique_together = ("parent_asset", "child_asset")
        verbose_name = "数据关联"
        verbose_name_plural = verbose_name


class ChangeRecord(StandardModelMixin, AuthorModelMixin):
    """资产变更记录表"""

    asset = models.ForeignKey(
        to=Asset,
        on_delete=models.CASCADE,
        related_name="record",
        verbose_name="关联资产数据",
    )
    title = models.CharField(max_length=64, verbose_name="变更字段名称")
    detail = models.CharField(max_length=1024, verbose_name="变更详情")

    class Meta:
        db_table = "pgo_data_map_asset_record"
        verbose_name = "变更记录"
        verbose_name_plural = verbose_name
