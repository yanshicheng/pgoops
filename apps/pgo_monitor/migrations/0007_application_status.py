# Generated by Django 3.2.13 on 2022-05-17 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pgo_monitor", "0006_auto_20220513_1729"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="status",
            field=models.BooleanField(default=True),
        ),
    ]
