from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
import signal
import sys
import time

class Command(BaseCommand):
    help = "Lance un scheduler APScheduler pour exécuter check_alerts toutes les heures."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()
        scheduler.add_job(lambda: call_command('check_alerts'), 'interval', hours=1)
        scheduler.add_job(lambda: call_command('fetch_latest_air'), 'interval', hours=1)
        scheduler.start()
        self.stdout.write(self.style.SUCCESS('APScheduler démarré.'))

        def shutdown(signum, frame):
            scheduler.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)

        # Boucle infinie pour garder le process actif
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()