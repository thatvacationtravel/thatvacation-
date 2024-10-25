import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from reservas.models import Itinerary

class Command(BaseCommand):
    help = 'Reemplaza todos los registros de itinerarios en la base de datos con los del archivo CSV y muestra el progreso.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta al archivo CSV con datos de itinerarios.')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']
        total_rows = sum(1 for row in csv.reader(open(csv_file_path, encoding='iso-8859-1'), delimiter=';')) - 1

        try:
            with open(csv_file_path, mode='r', encoding='iso-8859-1') as file:
                reader = csv.DictReader(file, delimiter=';')
                itineraries = []
                processed_rows = 0
                print_interval = 1000

                for row in reader:
                    itinerary = self.create_itinerary_from_row(row)
                    itineraries.append(itinerary)
                    processed_rows += 1

                    #
                    if processed_rows % print_interval == 0:
                        self.stdout.write(self.style.SUCCESS(f'Procesado {processed_rows} de {total_rows} registros.'), ending='\r')


                if processed_rows % print_interval != 0:
                    self.stdout.write(self.style.SUCCESS(f'Procesado {processed_rows} de {total_rows} registros.'), ending='\r')

                with transaction.atomic():
                    Itinerary.objects.all().delete()
                    Itinerary.objects.bulk_create(itineraries, batch_size=1000)
                    self.stdout.write(self.style.SUCCESS(f'\n{len(itineraries)} itinerarios han sido importados exitosamente.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la importación: {e}'))

            import logging
            logger = logging.getLogger(__name__)
            logger.error('Error durante la importación', exc_info=True)

    def create_itinerary_from_row(self, row):
        return Itinerary(
            cruise_id=row['CRUISE-ID'],
            departure_port=row['DEP-PORT'],
            departure_port_name=row['DEP-NAME-PORT'],
            departure_date=self.parse_date(row['DEP-DATE']),
            departure_day=int(row['DEP-DAY']),
            departure_weekday=row['DEP-WEEKDAY'],
            departure_time=row['DEP-TIME'],
            arrival_port=row['ARR-PORT'],
            arrival_port_name=row['ARR-NAME-PORT'],
            arrival_date=self.parse_date(row['ARR-DATE']),
            arrival_day=int(row['ARR-DAY']),
            arrival_weekday=row['ARR-WEEKDAY'],
            arrival_time=row['ARR-TIME'],
            itinerary_cd=row['ITIN-CD'],
            area_destination=row['AREA/DEST'],
            region_cd=row['REG-CD'],
            comm_area=row['COMM-AREA']
        )

    def parse_date(self, date_str, date_format='%d/%m/%y'):
        if date_str in ['N/A', '', None]:
            return None
        try:
            return datetime.strptime(date_str, date_format).date()
        except ValueError:
            return None
