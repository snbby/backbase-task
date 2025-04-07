from django.core.management.base import BaseCommand

from my_currency.utils import fill_currencies, fill_providers


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        fill_currencies()
        fill_providers()
