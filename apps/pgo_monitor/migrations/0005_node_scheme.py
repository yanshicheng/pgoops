# Generated by Django 3.2.13 on 2022-05-12 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pgo_monitor", "0004_group_grafana_path"),
    ]

    operations = [
        migrations.AddField(
            model_name="node",
            name="scheme",
            field=models.IntegerField(choices=[(0, "http"), (1, "https")], default=0),
        ),
    ]
