import csv
from django.core.management.base import BaseCommand
from reservas.models import Port  # Asegúrate de que el nombre de tu modelo y la app sean correctos
from tqdm import tqdm  # Asegúrate de instalar tqdm con `pip install tqdm`

class Command(BaseCommand):
    help = 'Importa y actualiza los puertos desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV con los datos de los puertos')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file_path']
        Port.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los puertos han sido eliminados.'))

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
            new_port = Port(
                port_code=row['PORT-CD'],
                port_name=row['PORT-NAME'],
                country_code=row.get('COUNTRY-CD', ''),
                country_name=row.get('COUNTRY-NAME', '')
            )
            to_create.append(new_port)

        batch_size = 1000

        for i in tqdm(range(0, len(to_create), batch_size), desc="Creando nuevos puertos"):
            batch = to_create[i:i + batch_size]
            Port.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS(f'Se han importado {len(to_create)} puertos desde el archivo CSV.'))
