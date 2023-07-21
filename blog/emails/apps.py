from django.apps import AppConfig


class EmailsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "emails"

    def ready(self):
        from emails.signals import on_reset_password_token_created
