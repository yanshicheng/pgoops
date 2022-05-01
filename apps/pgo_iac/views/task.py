from django.utils import timezone
from rest_framework.decorators import action

from common.file import File
from common.request_info import get_user, get_addr
from common.viewsets import StandardModelViewSet
from common.response import api_ok_response, api_error_response
from ..filters import TaskFilter
from ..models import Task, Repository
from ..serializers import TaskSerializer, TaskInfoSerializer
from ..tasks import rsync_task


class TaskModelViewSet(StandardModelViewSet):
    queryset = Task.objects.filter().order_by("-id")
    serializer_class = TaskSerializer
    ordering_fields = ("id",)
    filter_class = TaskFilter
    search_fields = ("name",)

    def create(self, request, *args, **kwargs):
        user = get_user(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repository_obj = Repository.objects.filter(id=request.data.get('repository')).first()
        if not File.if_file_exists(repository_obj.get_main_file()):
            return api_error_response('指定的仓库文件已经找不到，请重新确认。')
        instance = serializer.save(created_by=user, updated_by=user)
        # TaskRunner(instance).execute()
        celery_task = rsync_task.delay(instance.id, 'socket')
        instance.celery_id = celery_task.id
        instance.save()
        ws_url = f'ws://{request.META["HTTP_HOST"]}:{request.META["SERVER_PORT"]}/ws/iac/task/{instance.id}/'
        return api_ok_response({'ws_url': ws_url})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        return api_ok_response(TaskInfoSerializer(instance).data)

    @action(methods=["post"], detail=False, url_path='sync-task')
    def rsync_task(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repository_obj = Repository.objects.filter(id=request.data.get('repository')).first()
        if not File.if_file_exists(repository_obj.get_main_file()):
            return api_error_response('指定的仓库文件已经找不到，请重新确认。')

        instance: Task = serializer.save(created_by=get_user(request), updated_by=get_user(request))
        task = rsync_task.delay(instance.id)
        instance.celery_id = task.id
        instance.save()
        return api_ok_response(TaskSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance: Task = self.get_object()
        if instance.from_periodic:
            return api_error_response(f'定时任务执行记录不可删除，如需删除请先删除定时任务:{instance.from_periodic.name}')
        return super(TaskModelViewSet, self).destroy(request, *args, **kwargs)
