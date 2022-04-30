# Generated by Django 3.2.13 on 2022-04-29 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(help_text='名称', max_length=64, verbose_name='名称')),
                ('path', models.CharField(blank=True, max_length=128, null=True, verbose_name='api路径')),
                ('method', models.CharField(blank=True, max_length=128, null=True, verbose_name='请求方法')),
                ('pid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pgo_permission.rule')),
            ],
            options={
                'verbose_name': '权限规则',
                'verbose_name_plural': '权限规则',
                'db_table': 'pgo_permission_rules',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(help_text='名称', max_length=128, unique=True, verbose_name='名称')),
                ('rule', models.ManyToManyField(blank=True, related_name='role', to='pgo_permission.Rule', verbose_name='规则')),
            ],
            options={
                'verbose_name': '角色',
                'verbose_name_plural': '角色',
                'db_table': 'pgo_permission_role',
                'unique_together': {('name',)},
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('order', models.IntegerField(verbose_name='子菜单排序')),
                ('path', models.CharField(max_length=64, verbose_name='路由路径')),
                ('component', models.CharField(blank=True, max_length=128, null=True, verbose_name='视图路径')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='路由名')),
                ('title', models.CharField(blank=True, max_length=32, null=True, verbose_name='名称')),
                ('icon', models.CharField(blank=True, max_length=32, null=True, verbose_name='图标名')),
                ('redirect', models.CharField(blank=True, max_length=128, null=True, verbose_name='重定向')),
                ('active_menu', models.CharField(blank=True, max_length=128, null=True, verbose_name='详情路由')),
                ('hidden', models.BooleanField(default=False, verbose_name='隐藏')),
                ('always_show', models.BooleanField(default=True, verbose_name='显示根路由')),
                ('no_cache', models.BooleanField(default=False, verbose_name='不缓存')),
                ('breadcrumb', models.BooleanField(default=False, verbose_name='是否在面包屑显示')),
                ('affix', models.BooleanField(default=False, verbose_name='固定')),
                ('pid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pgo_permission.menu', verbose_name='父节点')),
                ('role', models.ManyToManyField(blank=True, to='pgo_permission.Role', verbose_name='权限角色')),
            ],
            options={
                'verbose_name': '前端菜单',
                'verbose_name_plural': '前端菜单',
                'db_table': 'pgo_permission_menu',
            },
        ),
    ]
