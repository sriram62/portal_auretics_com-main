from django.apps import AppConfig


class MlmAdminConfig(AppConfig):
    name = 'mlm_admin'

    def ready(self):
        import mlm_admin.signals