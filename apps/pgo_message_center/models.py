from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from rest_framework.exceptions import ValidationError

from common.models import StandardModelMixin
from common.message_provider import MessageProvider

__all__ = [
    "Provider",
    "Group",
    "Level",
    'History'
]


def message_provider_class(value: str) -> str:
    if value:
        try:
            clazz = import_string(value)
            if issubclass(clazz, MessageProvider):
                return value
        except:
            pass
        raise ValidationError("invalid alter provider class ")


message_provider_method = (
    (0, 'send_text_msg'),
    (1, 'send_markdown_msg'),
    (2, 'send_html_msg'),
    (3, 'send_file_msg'),
    (4, 'send_link_msg'),
    (5, 'send_image_msg'),
)


class Provider(StandardModelMixin):
    name = models.CharField(max_length=32, verbose_name='类型名称')
    provider_class = models.CharField(max_length=128, validators=[message_provider_class])
    method = models.IntegerField(choices=message_provider_method, default=1)

    def clean(self):
        super(Provider, self).clean()
        clazz = import_string(self.provider_class)
        if not hasattr(clazz, self.get_method_display()):
            raise ValidationError(f'{self.name} not {self.get_method_display()} method！')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_message_center_provider"
        verbose_name = "通知方式"
        unique_together = ('name', 'provider_class')
        verbose_name_plural = verbose_name


# relation

class Group(StandardModelMixin):
    name = models.CharField(max_length=32, unique=True, verbose_name='告警组')
    user = models.ManyToManyField(to=get_user_model(), verbose_name='分组人员')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_message_center_group"
        verbose_name = "通知组"
        verbose_name_plural = verbose_name


class Level(StandardModelMixin):
    name = models.CharField(max_length=32, unique=True, verbose_name='告警级别名')
    cname = models.CharField(max_length=32, unique=True)
    provider = models.ForeignKey(to=Provider, on_delete=models.PROTECT)
    group = models.ForeignKey(to=Group, on_delete=models.PROTECT)
    weight = models.IntegerField(unique=True)
    is_system = models.BooleanField(default=False)

    def get_email_list(self):
        return [u.email for u in self.group.user.all() if u.email]

    def get_phone_list(self):
        return [u.phone for u in self.group.user.all() if u.phone]

    def get_provider_class(self):
        return [p.provider_class for p in self.provider.all() if p.provider_class]

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_message_center_level"
        verbose_name = "通知级别"
        verbose_name_plural = verbose_name


class Types(models.IntegerChoices):
    firing = 0, '告警'
    resolved = 1, '告警恢复'
    notification = 2, '通 知'


status = (
    (0, '成功'),
    (1, '失败')
)


class History(StandardModelMixin):
    app_name = models.CharField(max_length=32, verbose_name='应  用')
    name = models.CharField(max_length=32, verbose_name='通告主题')
    type = models.IntegerField(choices=Types.choices, default=2, verbose_name="通告类型")
    level = models.ForeignKey(to=Level, on_delete=models.CASCADE, verbose_name='通告级别')
    status = models.IntegerField(choices=status, default=0, verbose_name='发送状态')
    instance = models.CharField(max_length=1024, blank=True, null=True, verbose_name='实例地址')
    labels = models.JSONField(verbose_name="扩展信息", blank=True, null=True)
    summary = models.CharField(max_length=1024, verbose_name="概要信息", blank=True, null=True)
    description = models.TextField(verbose_name="描述信息", blank=True, null=True)
    start_at = models.DateTimeField(verbose_name="开始时间", blank=True, null=True)
    end_at = models.DateTimeField(verbose_name="结束时间", blank=True, null=True)
    duration = models.CharField(verbose_name="持续时间", max_length=64, blank=True, null=True)
    output_err = models.TextField(blank=True, null=True)
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    repetition_num = models.IntegerField(default=1, verbose_name="重复次数")
    is_all = models.BooleanField(default=False)
    is_at = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "pgo_message_center_history"
        verbose_name = "通知历史"
        verbose_name_plural = "通知历史"

    def get_markdown_message(self, sign='\n'):
        msg = f'### **{History._meta.get_field("app_name").verbose_name}:** {self.app_name} ({self.get_type_display()}) {sign} ' \
              f'## **{History._meta.get_field("name").verbose_name}:** <font color=\"comment\">{self.name}</font> {sign} ' \
              f'--- {sign}' \
              f'> **{History._meta.get_field("level").verbose_name}:** <font color=\"comment\">{self.level.name} ({self.level.cname})</font> {sign}'
        if self.summary:
            msg += f'> **{History._meta.get_field("summary").verbose_name}:**  <font color=\"comment\">{self.summary}</font>{sign}'
        if self.instance:
            msg += f'> **{History._meta.get_field("instance").verbose_name}:**  <font color=\"comment\">{self.instance}</font>{sign}'
        if self.repetition_num:
            msg += f'> **{History._meta.get_field("repetition_num").verbose_name}:**  <font color=\"comment\">{self.repetition_num}</font>{sign}'
        if self.labels:

            labels_mess = ''
            # print(type(self.labels))
            for k, v in self.labels.items():
                labels_mess += f'>>> {k}:  <font color=\"comment\">{v}</font> {sign}'
            msg += f'> **{History._meta.get_field("labels").verbose_name}:** {sign} {labels_mess} {sign}'
        if self.description:
            msg += f'> **{History._meta.get_field("description").verbose_name}:**  <font color=\"comment\">{self.description}</font>{sign}'
        if self.start_at:
            msg += f'> **{History._meta.get_field("start_at").verbose_name}:**  <font color=\"comment\">{self.start_at}</font>{sign}'
        if self.end_at and self.type != 0:
            msg += f'> **{History._meta.get_field("end_at").verbose_name}:**  <font color=\"comment\">{self.end_at}</font>{sign}'
        if self.duration and self.type != 0:
            msg += f'> **{History._meta.get_field("duration").verbose_name}:**  <font color=\"comment\">{self.duration}</font>{sign}'
        if self.output_err:
            msg += f'> **{History._meta.get_field("output_err").verbose_name}:**  <font color=\"comment\">{self.output_err}</font>{sign}'

        return msg

    def get_text_message(self, sign='\n'):
        msg = f'{History._meta.get_field("app_name").verbose_name}: {self.app_name} ({self.get_type_display()}) {sign} ' \
              f'{History._meta.get_field("name").verbose_name}: {self.name} {sign} ' \
              f'------------------------------------------ {sign}' \
              f'{History._meta.get_field("level").verbose_name}: {self.level.name} ({self.level.cname}) {sign}'
        if self.summary:
            msg += f'{History._meta.get_field("summary").verbose_name}: {self.summary} {sign}'
        if self.instance:
            msg += f'{History._meta.get_field("instance").verbose_name}: {self.instance} {sign}'
        if self.repetition_num:
            msg += f'{History._meta.get_field("repetition_num").verbose_name}: {self.repetition_num} {sign}'
        if self.labels:
            msg += f'{History._meta.get_field("labels").verbose_name}: {self.labels} {sign}'
        if self.description:
            msg += f'{History._meta.get_field("description").verbose_name}: {self.description} {sign}'
        if self.start_at:
            msg += f'{History._meta.get_field("start_at").verbose_name}: {self.start_at} {sign}'
        if self.end_at and self.type != 0:
            msg += f'{History._meta.get_field("end_at").verbose_name}: {self.end_at} {sign}'
        if self.duration and self.type != 0:
            msg += f'{History._meta.get_field("duration").verbose_name}: {self.duration} {sign}'
        if self.output_err:
            msg += f'{History._meta.get_field("output_err").verbose_name}: {self.output_err} {sign}'

        return msg

    def get_html_message(self):
        msg = f'<tr>' \
              f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("app_name").verbose_name}</td>' \
              f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.app_name} ({self.get_type_display()}) </td>' \
              f'</tr>' \
              f'<tr>' \
              f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("name").verbose_name}</td>' \
              f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">  {self.name} </td>' \
              f'</tr>' \
              f'<tr>' \
              f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("level").verbose_name}</td>' \
              f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.level.name} ({self.level.cname}) </td>' \
              f'</tr>'
        if self.summary:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("summary").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.summary}</td>' \
                   f'</tr>'
        if self.instance:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("instance").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.instance} </td>' \
                   f'</tr>'
        if self.repetition_num:
            msg += f'' \
                   f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("repetition_num").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.repetition_num} </td>' \
                   f'</tr>'
        if self.labels:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("labels").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{self.labels} </td>' \
                   f'</tr>'
        if self.description:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("description").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{self.description}</td>' \
                   f'</tr>'
        if self.start_at:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("start_at").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.start_at} </td>' \
                   f'</tr>'
        if self.end_at and self.type != 0:
            msg += f'' \
                   f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("end_at").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.end_at}</td>' \
                   f'</tr>'
        if self.duration and self.type != 0:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("duration").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;"> {self.duration} </td>' \
                   f'</tr>'
        if self.output_err:
            msg += f'<tr>' \
                   f'<td class="column" style="font-weight: bold;background-color: #EFF3F6;color: #393C3E; height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{History._meta.get_field("output_err").verbose_name}</td>' \
                   f'<td style=" height: 35px;line-height: 35px;box-sizing: border-box;padding: 0 10px;border-bottom: 1px solid #E6EAEE;border-right: 1px solid #E6EAEE;">{self.output_err}</td>' \
                   f'</tr>'
        return msg

    @cached_property
    def get_provider_method(self):
        clazz = import_string(self.level.provider.provider_class)
        if issubclass(clazz, MessageProvider):
            return getattr(clazz(self), self.level.provider.get_method_display())


'''
"text":"### Spark application运行时间监控Test{sign}"
"> **Application_ID:** app-20201208100505-58622{sign}"
"> **Name:** compute_04{sign}"
"> **Duration:** 4.4 h"
'''
