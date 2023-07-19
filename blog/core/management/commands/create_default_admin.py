from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
import environ


class Command(BaseCommand):
    def handle(self, *args, **options):
        env = environ.Env()
        email = env.str("ADMIN_EMAIL", "") or None
        username = env.str("ADMIN_USERNAME")
        password = env.str("ADMIN_PASSWORD")

        User = get_user_model()
        User.objects.create_superuser(email=email, username=username, password=password)
