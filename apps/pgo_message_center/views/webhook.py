import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.status import HTTP_502_BAD_GATEWAY, HTTP_200_OK
from common.response import api_ok_response
from common.views import StandardOpenApiView, StandardApiView
from ..models import History, Level, Types
from ..tasks import parse_alertmanager


class WebHookBaseOpenApiView(StandardOpenApiView):
    history_model = History
    level_model = Level

    def firing(self, alert: dict):
        try:
            alert["level"] = self.get_level_model(alert["level"])
            old_obj = self.history_model.objects.filter(**alert).first()
            if old_obj:
                old_obj.repetition_num += 1
                old_obj.save()
            else:
                obj = self.history_model.objects.create(**alert)
                obj.save()
        except Exception as e:
            raise e

    def resolved(self, alert: dict):
        try:
            end_at = alert.pop("end_at")
            status = alert.pop("status")
            alert["level"] = self.get_level_model(alert["level"])
            old_obj = self.history_model.objects.filter(**alert).first()
            if old_obj:
                old_obj.duration = end_at - alert["start_at"]
                old_obj.status = status
                old_obj.save()
        except Exception as e:
            raise e

    def get_level_model(self, name):
        obj = self.level_model.objects.filter(name=name).first()
        if obj:
            return obj
        else:
            raise ObjectDoesNotExist(f"level 对象找不到: {name}")

    def parse(self, data_list: list):
        raise NotImplementedError(
            f"{self.__class__.__name__}, There is no implementation  parse  methods ，parameters data_list"
        )


class WebHookPromeOpenApiView(WebHookBaseOpenApiView):
    """
    通过token用户信息
    """

    def post(self, request, *args, **kwargs):
        try:
            parse_alertmanager.delay(request.data.get("alerts", []))
            return Response(data={"status": "success"}, status=HTTP_200_OK)
        except Exception as e:
            return Response(data="ok", status=HTTP_502_BAD_GATEWAY)

    def parse(self, data_list):
        item_list = []
        for item in data_list:
            instance = item["labels"].pop("instance")
            item_list.append(
                {
                    "app_name": "alertmanager",
                    "status": Types[f'{item.get("status")}'],
                    "name": item["labels"].pop("alertname"),
                    "instance": instance.split(":")[0],
                    "level": item["labels"].pop("severity"),
                    "summary": item["annotations"].get("summary"),
                    "description": item["annotations"].get("description"),
                    "labels": item["labels"],
                    "start_at": serializers.DateTimeField(
                        format="%Y-%m-%d %H:%M:%S.%f"
                    ).to_internal_value(item.get("startsAt")),
                    "end_at": serializers.DateTimeField(
                        format="%Y-%m-%d %H:%M:%S.%f"
                    ).to_internal_value(item.get("endsAt")),
                }
            )
        return item_list


# 'end_at': serializers.DateTimeField(item.get('startsAt')),
