from django.core.management.base import BaseCommand
from reservas.models import Item
from django.db import transaction

class Command(BaseCommand):
    help = 'Elimina todos los datos de la tabla Item en lotes de 1000 registros'

    def handle(self, *args, **kwargs):
        batch_size = 1000
        total_deleted = 0

        while True:
            with transaction.atomic():
                items = Item.objects.all()[:batch_size]
                if not items.exists():
                    break
                count = items.count()
                items_ids = list(items.values_list('id', flat=True))
                Item.objects.filter(id__in=items_ids).delete()
                total_deleted += count
                self.stdout.write(self.style.SUCCESS(f'{count} registros eliminados.'))

        self.stdout.write(self.style.SUCCESS(f'Total de registros eliminados: {total_deleted}'))
