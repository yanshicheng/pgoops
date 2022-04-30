from django.apps import AppConfig


class PgoMessageCenterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pgo_message_center'
    verbose_name = "告警通知中心"