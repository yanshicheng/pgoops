import celery
from celery import shared_task
from .models import Task, TaskState, TaskPeriodic
from apps.pgo_message_center.models import History
from .runner import TaskRunner
from pgoops import celery_app
from apps.pgo_message_center.tasks import notification_task


@celery_app.task()
def iac_message_center(task_id, status):
    task_obj = Task.objects.filter(celery_id=task_id).first()
    message_data = {
        "app_name": "iac",
        "name": task_obj.name,
        "level_id": 6,
        "status": status,
        "summary": "任务调度执行" if task_obj.from_periodic else "手动执行",
        "description": task_obj.describe,
        "start_at": task_obj.created_at,
        "end_at": task_obj.updated_at,
        "user": task_obj.created_by,
        "duration": task_obj.updated_at - task_obj.created_at,
        "labels": {
            "repository": task_obj.repository.name,
            "playbook": task_obj.playbook
            if task_obj.playbook
            else task_obj.repository.main,
            "forks": task_obj.forks,
            "timeout": task_obj.timeout,
        },
    }
    if task_obj.inventory and task_obj.inventory != "[]":
        message_data["labels"]["inventory"] = task_obj.inventory
    if task_obj.envvars and task_obj.envvars != {}:
        message_data["labels"]["envvars"] = task_obj.envvars
    if task_obj.extravars and task_obj.extravars != {}:
        message_data["labels"]["extravars"] = task_obj.extravars
    if task_obj.role and task_obj.role != "[]":
        message_data["labels"]["role"] = task_obj.role
    if task_obj.tags and task_obj.tags != "[]":
        message_data["labels"]["tags"] = task_obj.tags
    if task_obj.skip_tags and task_obj.skip_tags != "[]":
        message_data["labels"]["skip_tags"] = task_obj.skip_tags
    message_obj = History.objects.create(**message_data)
    notification_task.delay(message_obj.id)


class IacRsyncBaseTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        instance: Task = self.get_instance(args[0])
        if instance.alert:
            iac_message_center.delay(task_id, 0)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        instance: Task = self.get_instance(args[0])
        if instance.alert:
            iac_message_center.delay(task_id, 2)

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pass

    @staticmethod
    def get_instance(pk: int):
        return Task.objects.filter(id=pk).first()


@celery_app.task(bind=True, base=IacRsyncBaseTask)
def rsync_task(self, id: int, pattern=None):
    instance: Task = self.get_instance(id)
    instance.repository.run_num += 1
    instance.repository.save()
    if instance and instance.state == TaskState.PENDING:
        TaskRunner(instance, pattern).execute()


@shared_task()
def execute_periodic_task(id: int):
    task_periodic = TaskPeriodic.objects.filter(pk=id, enabled=True).first()
    if task_periodic:
        task_obj = Task.objects.create(
            name=task_periodic.name,
            repository=task_periodic.repository,
            playbook=task_periodic.playbook,
            inventory=task_periodic.inventory,
            envvars=task_periodic.envvars,
            extravars=task_periodic.extravars,
            forks=task_periodic.forks,
            timeout=task_periodic.timeout,
            role=task_periodic.role,
            tags=task_periodic.tags,
            skip_tags=task_periodic.skip_tags,
            from_periodic=task_periodic,
            created_by=task_periodic.created_by,
            updated_by=task_periodic.updated_by,
        )
        celery_task = rsync_task.delay(task_obj.id)
        task_obj.celery_id = celery_task.id
        task_obj.save()
