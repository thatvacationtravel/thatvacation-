import csv
from tqdm import tqdm
from reservas.models import City  # Asegúrate de reemplazar 'reservas' con el nombre de tu aplicación Django
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import cities data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        import_cities_from_csv(csv_file)

def import_cities_from_csv(csv_file):
    batch_size = 1000
    objects = []

    with open(csv_file, 'r', encoding='utf-8-sig', errors='ignore') as file:
        reader = csv.DictReader(file, delimiter=';')

        for row in reader:
            city_code = row['CITY-CD'].strip()
            city_name = row['CITY-NAME'].strip()
            country_code = row.get('COUNTRY-CD', '').strip()
            country_name = row.get('COUNTRY-NAME', '').strip()

            if country_name:  # Solo importa si country_name tiene valor
                city_obj = City(
                    city_code=city_code,
                    city_name=city_name,
                    country_code=country_code,
                    country_name=country_name
                )
                objects.append(city_obj)

            if len(objects) >= batch_size:
                City.objects.bulk_create(objects)
                objects = []

            # Final batch insert
        if objects:
            City.objects.bulk_create(objects)
