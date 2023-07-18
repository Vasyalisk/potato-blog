from django.core.management.commands import runserver
import time


class Command(runserver.Command):
    def handle(self, *args, **options):
        time.sleep(1)
        options["addrport"] = "0.0.0.0:8000"
        super().handle(*args, **options)
