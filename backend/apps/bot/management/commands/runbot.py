import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.core.management.base import BaseCommand
from apps.bot.handlers import run_bot


class Command(BaseCommand):
    help = 'Run the Telegram bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        try:
            run_bot()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Bot stopped'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
