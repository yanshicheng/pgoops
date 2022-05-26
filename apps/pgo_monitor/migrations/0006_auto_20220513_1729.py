# Generated by Django 3.2.13 on 2022-05-13 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pgo_data_map", "0004_alter_classify_icon"),
        ("pgo_monitor", "0005_node_scheme"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="asset",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="pgo_data_map.asset"
            ),
        ),
        migrations.AlterField(
            model_name="node",
            name="host",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to="pgo_data_map.asset"
            ),
        ),
        migrations.AlterField(
            model_name="rules",
            name="duration",
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name="rules",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="rules",
                to="pgo_monitor.group",
            ),
        ),
    ]
