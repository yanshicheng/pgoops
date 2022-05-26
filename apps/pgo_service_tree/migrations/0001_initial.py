# Generated by Django 3.2.13 on 2022-04-29 03:09

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NodeJoinTag",
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
                    "key",
                    models.CharField(db_index=True, max_length=32, verbose_name="Key"),
                ),
                ("value", models.JSONField(verbose_name="Value")),
            ],
            options={
                "verbose_name": "节点关联Tag",
                "verbose_name_plural": "节点关联Tag",
                "db_table": "pgo_service_tree_node_tag",
            },
        ),
        migrations.CreateModel(
            name="NodeLinkAsset",
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
                "verbose_name": "节点关联CMDB资产",
                "verbose_name_plural": "节点关联CMDB资产",
                "db_table": "pgo_service_tree_node_asset",
            },
        ),
        migrations.CreateModel(
            name="NodeLinkClassify",
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
                "verbose_name": "节点关联CMDB类型",
                "verbose_name_plural": "节点关联CMDB类型",
                "db_table": "pgo_service_tree_node_classify",
            },
        ),
        migrations.CreateModel(
            name="ServiceTree",
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
                    models.CharField(
                        db_index=True, max_length=100, verbose_name="节点名称-英文"
                    ),
                ),
                (
                    "name_cn",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="节点名称-中文"
                    ),
                ),
                (
                    "abspath",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="abspath"
                    ),
                ),
                (
                    "appkey",
                    models.CharField(
                        db_index=True, max_length=200, verbose_name="appkey"
                    ),
                ),
                ("lft", models.PositiveIntegerField(editable=False)),
                ("rght", models.PositiveIntegerField(editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(editable=False)),
                (
                    "parent",
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="pgo_service_tree.servicetree",
                        verbose_name="父级",
                    ),
                ),
            ],
            options={
                "verbose_name": "服务树基础表",
                "verbose_name_plural": "服务树基础表",
                "db_table": "pgo_service_tree",
            },
        ),
        migrations.CreateModel(
            name="NodeLinkOperaPermission",
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
                    "node",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pgo_service_tree.servicetree",
                        verbose_name="节点",
                    ),
                ),
            ],
            options={
                "verbose_name": "节点操作权限",
                "verbose_name_plural": "节点操作权限",
                "db_table": "pgo_service_tree_node_permission",
            },
        ),
    ]
