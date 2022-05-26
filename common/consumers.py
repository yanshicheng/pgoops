from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from apps.pgo_iac.models import Task


class StandardAsyncJsonModelChangedConsumer(AsyncJsonWebsocketConsumer):
    model = None
    serializer_class = None
    url_route_name = "pk"

    def __init__(self, *args, **kwargs):
        super(StandardAsyncJsonModelChangedConsumer, self).__init__(*args, **kwargs)
        self.pk = None
        self.group_name = None

    def get_queryset(self):
        return self.model.objects.filter(pk=self.pk)

    @database_sync_to_async
    def get_object(self):
        return self.get_queryset().first()

    @classmethod
    @database_sync_to_async
    def encode_object(cls, instance):
        return cls.serializer_class(instance).data

    async def connect(self):  # on_open  对端建立链接
        self.pk = int(self.scope["url_route"]["kwargs"][self.url_route_name])
        self.group_name = await self.model.channel_layer_group_name(self.pk)
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def on_changed(self, event):
        instance: Task = await self.get_object()

        if instance:
            data = await self.encode_object(instance)
            await self.send_json(data)
            if instance.state != 1 and instance.state != 2:
                await self.disconnect("code")


# /connect ws://127.0.0.1:8000/ws/iac/task/1/
