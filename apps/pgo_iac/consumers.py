from channels.generic.websocket import WebsocketConsumer

from apps.pgo_iac.models import Task
from apps.pgo_iac.serializers import TaskSerializer
from common.consumers import StandardAsyncJsonModelChangedConsumer


class AsyncTaskEventConsumer(StandardAsyncJsonModelChangedConsumer):
    model = Task
    serializer_class = TaskSerializer
