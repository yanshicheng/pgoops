import ast
import datetime
import json
import os.path

import simplejson
from django.db import models
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule

from common.authmodel import AuthorModelMixin
from common.file import File
from common.models import StandardModelMixin, BroadcastModelMixin

data_time = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')


class Repository(StandardModelMixin, AuthorModelMixin):
    project_name = models.CharField(max_length=20, null=True, blank=True, db_index=True, verbose_name='项目名')
    name = models.CharField(max_length=40, verbose_name='项目入口包名称', unique=True, )
    main = models.CharField(max_length=20, verbose_name='入口文件', default='deploy.yaml')
    describe = models.CharField(max_length=60, null=True, blank=True, verbose_name='描述')
    run_num = models.IntegerField(default=0, verbose_name='运行次数')

    class Meta:
        db_table = "pgo_iac_repository"
        verbose_name = verbose_name_plural = "仓库中心"

    def __str__(self):
        return self.name

    def get_package_path(self):
        return os.path.join(settings.MEDIA_ROOT, settings.IAC_WORK_DIR, self.name)

    def get_main_file(self):
        return os.path.join(self.get_package_path(), 'project', self.main)

    def get_hosts_base_path(self):
        return os.path.join(self.get_package_path(), 'inventory')

    def get_hosts(self):
        return os.path.join(self.get_package_path(), 'inventory', 'hosts')


class TaskState(models.IntegerChoices):
    PENDING = 0, 'PENDING'
    RUNNING = 1, 'RUNNING'
    COMPLETED = 2, 'COMPLETED'
    FAILED = 3, 'FAILED'
    CANCELED = 4, 'CANCELED'
    TIMEOUT = 5, 'TIMEOUT'


class BaseTaskModelMixin(StandardModelMixin, AuthorModelMixin):
    repository = models.ForeignKey(to=Repository, on_delete=models.RESTRICT, verbose_name='关联仓库项目')
    playbook = models.CharField(max_length=30, null=True, blank=True)
    inventory = models.TextField(null=True, blank=True, verbose_name='主机列表')
    envvars = models.JSONField(null=True, blank=True, verbose_name='变量')
    extravars = models.JSONField(null=True, blank=True, verbose_name='环境变量')
    forks = models.IntegerField(default=1, blank=True, verbose_name='并发数')
    timeout = models.IntegerField(default=3600, verbose_name='超时时间')
    role = models.CharField(max_length=30, null=True, blank=True, verbose_name='执行的角色列表')
    tags = models.CharField(max_length=30, null=True, blank=True, verbose_name='执行的tag')
    skip_tags = models.CharField(max_length=30, null=True, blank=True, verbose_name='跳过的 tag')
    alert = models.BooleanField(default=True)

    class Meta:
        abstract = True


TaskMethod = ((0, "手动执行"), (1, "任务计划"))


class TaskPeriodic(BaseTaskModelMixin):
    name = models.CharField(max_length=200)
    interval = models.ForeignKey(IntervalSchedule, on_delete=models.CASCADE, null=True)
    crontab = models.ForeignKey(CrontabSchedule, on_delete=models.CASCADE, null=True)
    enabled = models.BooleanField(default=True)
    beat = models.ForeignKey(PeriodicTask, on_delete=models.CASCADE, null=True)
    describe = models.CharField(max_length=100, null=True, blank=True, verbose_name='描述')

    def save(self, *args, **kwargs):
        super(TaskPeriodic, self).save(*args, **kwargs)
        if self.beat:
            self.beat.interval = self.interval
            self.beat.crontab = self.crontab
            self.beat.enabled = self.enabled
            self.beat.args = json.dumps([self.id])
            self.beat.save()
        else:
            self.beat = PeriodicTask.objects.create(
                name=self.name,
                task='apps.pgo_iac.tasks.execute_periodic_task',
                interval=self.interval,
                crontab=self.crontab,
                enabled=self.enabled,
                args=json.dumps([self.id])
            )
            self.save_base()

    class Meta:
        db_table = "pgo_iac_task_periodic"
        verbose_name = verbose_name_plural = "周期性任务"


class Task(BroadcastModelMixin, BaseTaskModelMixin):
    name = models.CharField(max_length=30, verbose_name='执行任务名', db_index=True)
    celery_id = models.CharField(max_length=36, verbose_name='celery_id', null=True, blank=True)
    state = models.IntegerField(choices=TaskState.choices, default=TaskState.PENDING, verbose_name='任务执行状态')
    output = models.TextField(null=True, blank=True, verbose_name='任务输出')
    from_periodic = models.ForeignKey(TaskPeriodic, on_delete=models.CASCADE, null=True, related_name='task')
    describe = models.CharField(max_length=100, null=True, blank=True, verbose_name='描述')

    class Meta:
        db_table = "pgo_iac_task"
        verbose_name = verbose_name_plural = "仓库中心"

    def __str__(self):
        return self.name

    @staticmethod
    def _load(text):
        if text is None:
            return
        try:
            return simplejson.loads(text)
        except Exception:
            return

    @staticmethod
    def _load_list(text):
        if not text:
            return
        try:
            tmp_text = ast.literal_eval(text)
            if type(tmp_text) == list:
                if tmp_text:
                    return tmp_text
                else:
                    return None
        except Exception:
            return None

    def to_runner_kwargs(self):
        kwargs = {
            'playbook': self.repository.main,
            'forks': self.forks,
            'timeout': self.timeout
        }
        envvars = self._load(self.envvars)
        if envvars:
            kwargs['envvars'] = envvars
        extravars = self._load(self.extravars)
        if extravars:
            kwargs['extravars'] = extravars
        role = self._load_list(self.role)
        if role:
            kwargs['role'] = role
        tags = self._load_list(self.tags)
        if tags:
            kwargs['tags'] = tags
        skip_tags = self._load_list(self.skip_tags)
        if skip_tags:
            kwargs['skip_tags'] = skip_tags
        inventory = self._load_list(self.inventory)
        if inventory:
            kwargs['inventory'] = self._save_inventory(inventory)
        return kwargs

    def _save_inventory(self, inventory_list):
        abs_path = os.path.join(self.repository.get_package_path(), 'tmp_inventory')
        if not File.if_dir_exists(abs_path):
            File.create_dir(abs_path)
        file_name = f'{self.name}'
        file_path = os.path.join(abs_path, file_name)
        with open(file_path, 'w+', encoding='utf-8') as f:
            for inventory in inventory_list:
                f.writelines(f'{inventory}\n')
            # yaml.dump(inventory_list, f, default_flow_style=False, encoding='utf-8', allow_unicode=True)
        return [f'../tmp_inventory/{file_name}']


class EventState(models.IntegerChoices):
    OK = 0, 'ok'
    FAILED = 1, 'failed'
    SKIPPED = 2, 'skipped'
    UNREACHABLE = 3, 'unreachable'


class TaskEvent(StandardModelMixin, models.Model):
    task_record = models.ForeignKey(Task, on_delete=models.PROTECT)
    state = models.IntegerField(choices=EventState.choices)
    play = models.CharField(max_length=512)
    task = models.CharField(max_length=512)
    host = models.CharField(max_length=512)
    ip = models.GenericIPAddressField(null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    duration = models.FloatField()
    changed = models.BooleanField()
    detail = models.JSONField()

    class Meta:
        db_table = "pgo_iac_task_event"
        verbose_name = verbose_name_plural = "任务事件"

    def __str__(self):
        return self.host


class TaskStats(StandardModelMixin):
    task_record = models.ForeignKey(Task, on_delete=models.PROTECT)
    host = models.CharField(max_length=512)
    ip = models.GenericIPAddressField(null=True)
    ok = models.IntegerField(default=0)
    changed = models.IntegerField(default=0)
    dark = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)
    ignored = models.IntegerField(default=0)
    rescued = models.IntegerField(default=0)
    skipped = models.IntegerField(default=0)

    class Meta:
        db_table = "pgo_iac_task_stats"
        verbose_name = verbose_name_plural = "任务状态概览"

    def __str__(self):
        return self.host

# post_save.connect(model_changed, sender=Task)
