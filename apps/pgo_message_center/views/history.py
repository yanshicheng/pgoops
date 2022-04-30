from django.utils import timezone
from django.utils.datetime_safe import datetime
from rest_framework.decorators import action
from common.response import api_ok_response, api_error_response
from common.viewsets import StandardModelViewSet
from common.request_info import get_user, get_user_name
from ..models import History, Provider, Level
from ..serializers import HistorySerializers


class HistoryModelViewSet(StandardModelViewSet):
    queryset = History.objects.filter().order_by('-id')
    serializer_class = HistorySerializers
    ordering_fields = ("-id",)
    filter_fields = ("name",)
    search_fields = ("name",)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: History = serializer.save(request=request)
        try:
            instance.get_provider_method()
            return api_ok_response(HistorySerializers(instance).data)
        except Exception as e:
            instance.status = 1
            instance.output_err = str(e)
            return api_error_response(f'通知发送失败: {e}')

    def update(self, request, *args, **kwargs):
        return api_error_response('禁止更新')


    @action(methods=["post"], detail=False)
    def test(self, request, *args, **kwargs):
        level_id = request.data.get('level_id', '')
        if not level_id:
            return api_error_response('level_id 为必传参数')
        level_obj = Level.objects.filter(id=level_id).first()
        if not level_obj:
            return api_error_response('找不到通知等级实例，请检查ID是否正确！')
        data = {
            'app_name': 'message_center',
            'name': '通知测试-pgoops自动化运维平台',
            'type': 2,
            'level': level_obj,
            'instance': '0.0.0.0',
            'labels': {'user': get_user_name(request), 'app': 'message_center'},
            'summary': '这是一条测试消息！',
            'description': f'这是来自: {get_user_name(request)},发起的测试消息。\n 官网地址: www.pgoops.com',
            'start_at': datetime.now(),
            'end_at': datetime.now(),
            'duration': '00:00:00',
            'user': get_user(request)
        }
        object = History.objects.create(**data)
        try:
            object.get_provider_method()
            return api_ok_response('测试消息发送成功')
        except Exception as e:
            object.status = 1
            object.output_err = str(e)
            object.save()
            return api_error_response(f'测试消息发送失败:{str(e)}')
