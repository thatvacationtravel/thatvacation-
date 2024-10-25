from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Eliminar todos los datos de la tabla Item'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE reservas_item;')
        self.stdout.write(self.style.SUCCESS('Todos los datos han sido eliminados de la tabla Item.'))