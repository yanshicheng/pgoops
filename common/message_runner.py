from apps.pgo_message_center.models import History


class AlterManager:
    def __init__(self, instance: History):
        self.instance = instance

    def get_email_list(self):
        return self.instance.level.get_email_list()

    def get_phone_list(self):
        return self.instance.level.get_email_list()

    def get_provider_class(self):
        return self.instance.level.get_provider_class()
