import time

from django.core.management.commands import runserver
from django.db import OperationalError, connection


class Command(runserver.Command):
    def handle(self, *args, **options):
        self.retry_db_connection()
        options["addrport"] = "0.0.0.0:8000"
        super().handle(*args, **options)

    def check_db_connection(self):
        try:
            connection.ensure_connection()
            return True, None
        except OperationalError as e:
            return False, e

    def retry_db_connection(self, attempts=10, attempt_delay=1):
        for _ in range(attempts):
            is_connected, error = self.check_db_connection()

            if is_connected:
                return

            time.sleep(attempt_delay)

        # noinspection PyUnboundLocalVariable
        raise error
