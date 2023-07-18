from django.core.management.commands import runserver
import time


class Command(runserver.Command):
    def handle(self, *args, **options):
        time.sleep(1)
        super().handle(*args, **options)
