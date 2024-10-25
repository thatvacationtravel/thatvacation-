import csv
from django.core.management.base import BaseCommand
from reservas.models import Region  # Asegúrate de que el nombre de tu modelo y la app sean correctos
from tqdm import tqdm  # Asegúrate de instalar tqdm con `pip install tqdm`

class Command(BaseCommand):
    help = 'Importa y actualiza las regiones desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV con los datos de las regiones')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file_path']
        Region.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todas las regiones han sido eliminadas.'))

        try:
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                rows = list(reader)
        except UnicodeDecodeError:
            with open(path, newline='', encoding='latin-1') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                rows = list(reader)

        to_create = []

        for row in tqdm(rows, desc="Procesando filas del CSV"):
            region_code = row['CITY-CD']
            region_description = row['CITY-NAME']

            new_region = Region(
                region_code=region_code,
                region_description=region_description
            )
            to_create.append(new_region)

        batch_size = 1000

        for i in tqdm(range(0, len(to_create), batch_size), desc="Creando nuevas regiones"):
            batch = to_create[i:i + batch_size]
            Region.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS(f'Se han importado {len(to_create)} regiones desde el archivo CSV.'))
