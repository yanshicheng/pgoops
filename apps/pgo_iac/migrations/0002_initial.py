# Generated by Django 3.2.13 on 2022-04-29 03:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("django_celery_beat", "0015_edit_solarschedule_events_choices"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pgo_iac", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskperiodic",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="taskperiodic",
            name="crontab",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_celery_beat.crontabschedule",
            ),
        ),
        migrations.AddField(
            model_name="taskperiodic",
            name="interval",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="django_celery_beat.intervalschedule",
            ),
        ),
        migrations.AddField(
            model_name="taskperiodic",
            name="repository",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="pgo_iac.repository",
                verbose_name="关联仓库项目",
            ),
        ),
        migrations.AddField(
            model_name="taskperiodic",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="taskevent",
            name="task_record",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="pgo_iac.task"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="from_periodic",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="task",
                to="pgo_iac.taskperiodic",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="repository",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="pgo_iac.repository",
                verbose_name="关联仓库项目",
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="repository",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="repository",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
