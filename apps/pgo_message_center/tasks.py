from abc import ABC
from django.utils.module_loading import import_string
import celery
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from pgoops import celery_app
from .models import History, Level, Types


class MessageCenterBaseTask(celery.Task):
    def on_success(self, retval, task_id, args, kwargs):
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        instance = self.get_instance(args[0])
        instance.output_err = str(exc)
        instance.status = 1
        instance.save()
    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pass

    @staticmethod
    def get_instance(pk: int):
        return History.objects.filter(id=pk).first()
    # filter=task_method


@celery_app.task(bind=True, base=MessageCenterBaseTask)
def notification_task(self, pk: int):
    instance = self.get_instance(pk)
    instance.get_provider_method()


class AlertmanagerBaseTask(celery.Task):
    level_model = Level
    history_model = History

    def on_success(self, retval, task_id, args, kwargs):
        # task_obj = History.objects.filter(task_id=task_id).first()
        pass

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # task_obj = History.objects.filter(task_id=task_id).first()
        pass

    # 任务重试时执行
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        pass

    def firing(self, alert: dict):
        try:
            alert['level'] = self.get_level_model(alert['level'])
            obj = self.history_model.objects.filter(**alert).first()
            if obj:
                obj.repetition_num += 1
                obj.save()
            else:
                obj = self.history_model.objects.create(**alert)
                obj.save()
            notification_task.delay(obj.id)
        except Exception as e:
            raise e

    def resolved(self, alert: dict):
        try:
            end_at = alert.pop('end_at')
            status = alert.pop('status')
            alert['level'] = self.get_level_model(alert['level'])
            old_obj = self.history_model.objects.filter(**alert).first()
            if old_obj:
                old_obj.duration = end_at - alert['start_at']
                old_obj.status = status
                old_obj.save()
                notification_task.delay(old_obj.id)
        except Exception as e:
            raise e

    def get_level_model(self, name):
        obj = self.level_model.objects.filter(name=name).first()
        if obj:
            return obj
        else:
            raise ObjectDoesNotExist(f'level 对象找不到: {name}')


@celery_app.task(bind=True, base=AlertmanagerBaseTask)
def parse_alertmanager(self, data_list: dict):
    item_list = []

    for item in data_list:
        print(item.get("status"))
        instance = item['labels'].pop('instance')
        item_list.append({
            'app_name': 'alertmanager',
            'status': Types[f'{item.get("status")}'],
            'name': item['labels'].pop('alertname'),
            'instance': instance.split(':')[0],
            'level': item['labels'].pop('severity'),
            'summary': item['annotations'].get('summary'),
            'description': item['annotations'].get('description'),
            'labels': item['labels'],
            'start_at': serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f").to_internal_value(
                item.get('startsAt')),
            'end_at': serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S.%f").to_internal_value(item.get('endsAt'))
        })
    for alert in item_list:
        if alert['status'] == 0:
            self.firing(alert)
        elif alert['status'] == 1:
            self.resolved(alert)
