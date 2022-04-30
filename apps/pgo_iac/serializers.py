import ast

from django_celery_beat.models import IntervalSchedule, CrontabSchedule
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import Repository, Task, TaskStats, TaskEvent, TaskPeriodic, BaseTaskModelMixin
from common.serializers import StandardModelSerializer


class BaseTaskModelMixinSerializer(StandardModelSerializer):
    inventory = serializers.ListField()
    tags = serializers.ListField()
    skip_tags = serializers.ListField()
    role = serializers.ListField()

    class Meta:
        model = BaseTaskModelMixin
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(BaseTaskModelMixinSerializer, self).to_representation(instance)
        representation['repository_name'] = instance.repository.project_name
        representation['playbook'] = instance.playbook if instance.playbook else instance.repository.main
        try:
            representation['inventory'] = ast.literal_eval(instance.inventory)
        except Exception:
            representation['inventory'] = []
        try:
            representation['role'] = ast.literal_eval(instance.role)
        except Exception:
            representation['role'] = []
        try:
            representation['skip_tags'] = ast.literal_eval(instance.skip_tags)
        except Exception:
            representation['skip_tags'] = []
        try:
            representation['tags'] = ast.literal_eval(instance.tags)
        except Exception:
            representation['tags'] = []

        return representation


class RepositorySerializer(StandardModelSerializer):
    name = serializers.CharField(read_only=True)
    site = serializers.CharField(read_only=True)
    code_package = serializers.FileField(write_only=True, required=True)

    class Meta:
        model = Repository
        # fields = ('code_package', 'site', 'name')
        fields = '__all__'

    # def validate(self, attrs):
    #     code_package = attrs.pop('code_package')  # 必须pop出来，不能存入数据库中
    #
    #     package_name = PrepareHandler(code_package).save()
    #     attrs['name'] = package_name
    #     return attrs

    def create(self, validated_data):
        validated_data.pop('code_package')
        return super(RepositorySerializer, self).create(validated_data)


class TaskStatsSerializer(StandardModelSerializer):
    class Meta:
        model = TaskStats
        fields = '__all__'


class TaskEventSerializer(StandardModelSerializer):
    class Meta:
        model = TaskEvent
        fields = '__all__'


class TaskSerializer(BaseTaskModelMixinSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(TaskSerializer, self).to_representation(instance)
        representation['state'] = instance.get_state_display()
        return representation

    def validate(self, attrs):
        return attrs


class TaskInfoSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def to_representation(self, instance):
        representation = super(TaskInfoSerializer, self).to_representation(instance)
        representation['state'] = instance.get_state_display()
        representation['repository'] = RepositorySerializer(instance.repository).data
        representation['task_stats'] = TaskStatsSerializer(TaskStats.objects.filter(task_record=instance.id),
                                                           many=True).data
        return representation


class IntervalSerializer(StandardModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabSerializer(StandardModelSerializer):
    timezone = TimeZoneSerializerField()

    class Meta:
        model = CrontabSchedule
        fields = '__all__'


class TaskPeriodicSerializer(BaseTaskModelMixinSerializer):
    interval = IntervalSerializer(required=False)
    crontab = CrontabSerializer(required=False)

    # release = ReleaseSummarySerializer()

    class Meta:
        model = TaskPeriodic
        exclude = ['beat']

    def validate(self, attrs):
        schedule_types = ['interval', 'crontab']
        selected_schedule_types = [s for s in schedule_types if attrs.get(s)]
        if len(selected_schedule_types) > 1:
            raise serializers.ValidationError("Only one of interval or crontab must be set.")
        return attrs

    @classmethod
    def _update_child(cls, model, data):
        if data:
            pk = data.pop("id", None)
            instance = model.objects.filter(pk=pk)
            if instance:
                for k, v in data.items():
                    setattr(instance, k, v)
                instance.save()
                return instance
            else:
                return model.objects.create(**data)

    def create(self, validated_data):
        interval = validated_data.pop('interval', None)
        if interval:
            validated_data['interval'] = IntervalSchedule.objects.create(**interval)
        crontab = validated_data.pop('crontab', None)
        if crontab:
            validated_data['crontab'] = CrontabSchedule.objects.create(**crontab)
        return TaskPeriodic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        interval = self._update_child(IntervalSchedule, validated_data.pop('interval', None))
        crontab = self._update_child(CrontabSchedule, validated_data.pop('crontab', None))
        if interval:
            instance.crontab = None
            instance.interval = interval
        if crontab:
            instance.interval = None
            instance.crontab = crontab
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
