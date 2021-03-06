# Generated by Django 3.2.13 on 2022-05-25 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pgo_message_center", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="provider",
            name="icon",
            field=models.ImageField(
                blank=True,
                default="data_map/icon/2021/08/19/pgoops.png",
                null=True,
                upload_to="data_map/icon/%Y/%m/%d/",
                verbose_name="图标",
            ),
        ),
    ]
