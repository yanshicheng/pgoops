# Generated by Django 3.2.13 on 2022-04-29 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Asset",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                ("data", models.JSONField(default=dict, verbose_name="数据值")),
                ("ban_bind", models.BooleanField(default=False, verbose_name="禁止绑定")),
            ],
            options={
                "verbose_name": "表数据",
                "verbose_name_plural": "表数据",
                "db_table": "pgo_data_map_asset",
            },
        ),
        migrations.CreateModel(
            name="AssetBind",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "数据关联",
                "verbose_name_plural": "数据关联",
                "db_table": "pgo_data_map_asset_bind",
            },
        ),
        migrations.CreateModel(
            name="ChangeRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                ("title", models.CharField(max_length=64, verbose_name="变更字段名称")),
                ("detail", models.CharField(max_length=1024, verbose_name="变更详情")),
            ],
            options={
                "verbose_name": "变更记录",
                "verbose_name_plural": "变更记录",
                "db_table": "pgo_data_map_asset_record",
            },
        ),
        migrations.CreateModel(
            name="Classify",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "name",
                    models.CharField(max_length=32, unique=True, verbose_name="名称"),
                ),
                (
                    "alias",
                    models.CharField(
                        blank=True,
                        max_length=32,
                        null=True,
                        unique=True,
                        verbose_name="别名",
                    ),
                ),
                (
                    "icon",
                    models.ImageField(
                        blank=True, null=True, upload_to="cmdb/icon/%Y/%m/%d/"
                    ),
                ),
                (
                    "record_log",
                    models.BooleanField(default=False, verbose_name="是否记录日志"),
                ),
                ("ban_bind", models.BooleanField(default=False, verbose_name="是否允许绑定")),
            ],
            options={
                "verbose_name": "表分类",
                "verbose_name_plural": "表分类",
                "db_table": "pgo_data_map_classify",
            },
        ),
        migrations.CreateModel(
            name="ClassifyBind",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "bind_mode",
                    models.BooleanField(default=True, verbose_name="是ForeignKey"),
                ),
            ],
            options={
                "verbose_name": "表关联",
                "verbose_name_plural": "表关联",
                "db_table": "pgo_data_map_classify_bind",
            },
        ),
        migrations.CreateModel(
            name="Fields",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                ("fields", models.JSONField(default=dict, verbose_name="字段元数据")),
                ("rules", models.JSONField(default=dict, verbose_name="字段验证规则")),
                (
                    "classify",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fields",
                        to="pgo_data_map.classify",
                        verbose_name="关联Classify",
                    ),
                ),
            ],
            options={
                "verbose_name": "表字段",
                "verbose_name_plural": "表字段",
                "db_table": "pgo_data_map_fields",
            },
        ),
    ]
