import time

from django.core.management import BaseCommand, CommandParser
from django.db import OperationalError, connection


class Command(BaseCommand):
    help = "Ensures that all required application connections are intact"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--attempts", "-a", default=10)
        parser.add_argument("--delay", "-d", default=1, help="Delay in seconds between attempts")

    def handle(self, *args, **options):
        self.retry_db_connection(attempts=options["attempts"], attempt_delay=options["delay"])

    def check_db_connection(self):
        try:
            connection.ensure_connection()
            return True, None
        except OperationalError as e:
            return False, e

    def retry_db_connection(self, attempts, attempt_delay):
        for _ in range(attempts):
            is_connected, error = self.check_db_connection()

            if is_connected:
                return

            time.sleep(attempt_delay)

        # noinspection PyUnboundLocalVariable
        raise error
