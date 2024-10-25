import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from reservas.models import cabinDetail  # Asegúrate de que el nombre de tu modelo y la app sean correctos
from tqdm import tqdm  # Asegúrate de instalar tqdm con `pip install tqdm`

class Command(BaseCommand):
    help = 'Importa y actualiza detalles de cabinas desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV con los datos de las cabinas')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file_path']
        cabinDetail.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los detalles de cabinas han sido eliminados.'))

        existing_cabins = cabinDetail.objects.all()
        existing_cabins_dict = {(cabin.cabin_number, cabin.ship_name): cabin for cabin in existing_cabins}

        to_create = []
        to_update = []
        updated_cabins_keys = set()

        with open(path, newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            rows = list(reader)
            for row in tqdm(rows, desc="Procesando filas del CSV"):
                key = (row['CABIN NUMBER'], row['SHIP-NAME'])
                updated_cabins_keys.add(key)
                if key in existing_cabins_dict:
                    cabin = existing_cabins_dict[key]
                    cabin.ship_cd = row['SHIP-CD']
                    cabin.category_code = row['CATEGORY CODE']
                    cabin.category_desc = row['CATEGORY DESC']
                    cabin.min_occupancy = int(row['MIN OCCUPANCY']) if row['MIN OCCUPANCY'] != 'N/A' else 1
                    cabin.max_occupancy = int(row.get('MAX OCCUPANCY', '1')) if row['MAX OCCUPANCY'] != 'N/A' else 1
                    cabin.physically_challenged = row.get('PHYSICALLY CHALLENGED', 'no')
                    cabin.deck_code = row.get('DECK CODE', 'N/A')
                    cabin.deck_desc = row.get('DECK DESC', 'N/A')
                    cabin.start_date_validation = parse_date(row.get('START DATE VALIDATION', '')) if row['START DATE VALIDATION'] != 'N/A' else None
                    cabin.end_date_validation = parse_date(row.get('END DATE VALIDATION', '')) if row['END DATE VALIDATION'] != 'N/A' else None
                    cabin.obs_view = row.get('OBS-VIEW', 'N/A')
                    cabin.bed_arrmnt = row.get('BED-ARRMNT', 'N/A')

                    to_update.append(cabin)
                else:
                    new_cabin = cabinDetail(
                        cabin_number=row['CABIN NUMBER'],
                        ship_name=row['SHIP-NAME'],
                        ship_cd=row['SHIP-CD'],
                        category_code=row['CATEGORY CODE'],
                        category_desc=row['CATEGORY DESC'],
                        min_occupancy=int(row['MIN OCCUPANCY']) if row['MIN OCCUPANCY'] != 'N/A' else 1,
                        max_occupancy=int(row.get('MAX OCCUPANCY', '1')) if row['MAX OCCUPANCY'] != 'N/A' else 1,
                        physically_challenged=row.get('PHYSICALLY CHALLENGED', 'no'),
                        deck_code=row.get('DECK CODE', 'N/A'),
                        deck_desc=row.get('DECK DESC', 'N/A'),
                        start_date_validation=parse_date(row.get('START DATE VALIDATION', '')) if row['START DATE VALIDATION'] != 'N/A' else None,
                        end_date_validation=parse_date(row.get('END DATE VALIDATION', '')) if row['END DATE VALIDATION'] != 'N/A' else None,
                        obs_view=row.get('OBS-VIEW', 'N/A'),
                        bed_arrmnt=row.get('BED-ARRMNT', 'N/A'),
                    )
                    to_create.append(new_cabin)

        batch_size = 1000

        for i in tqdm(range(0, len(to_create), batch_size), desc="Creando nuevas cabinas"):
            batch = to_create[i:i + batch_size]
            cabinDetail.objects.bulk_create(batch)

        update_fields = ['ship_cd', 'category_code', 'category_desc', 'min_occupancy', 'max_occupancy', 'physically_challenged', 'deck_code', 'deck_desc', 'start_date_validation', 'end_date_validation', 'obs_view', 'bed_arrmnt']
        for i in tqdm(range(0, len(to_update), batch_size), desc="Actualizando cabinas"):
            batch = to_update[i:i + batch_size]
            cabinDetail.objects.bulk_update(batch, update_fields)

        to_delete_keys = set(existing_cabins_dict.keys()) - updated_cabins_keys
        if to_delete_keys:
            to_delete = [existing_cabins_dict[key].id for key in to_delete_keys]
            cabinDetail.objects.filter(id__in=to_delete).delete()
            self.stdout.write(self.style.SUCCESS(f'Eliminadas {len(to_delete)} cabinas no listadas en el CSV.'))

        self.verify_data_consistency(path)

    def verify_data_consistency(self, csv_file_path):
        with open(csv_file_path, newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            csv_data_set = {(row['CABIN NUMBER'], row['SHIP-NAME']) for row in reader}
        db_data_set = {(cabin.cabin_number, cabin.ship_name) for cabin in cabinDetail.objects.all()}

        if len(csv_data_set) == len(db_data_set):
            self.stdout.write(self.style.SUCCESS('El número de registros coincide entre el CSV y la base de datos.'))
        else:
            self.stdout.write(self.style.ERROR('El número de registros NO coincide entre el CSV y la base de datos.'))

        if csv_data_set.issubset(db_data_set):
            self.stdout.write(self.style.SUCCESS('Todos los registros del CSV están presentes en la base de datos.'))
        else:
            missing_in_db = csv_data_set - db_data_set
            self.stdout.write(self.style.ERROR(f'Registros faltantes en la base de datos: {missing_in_db}'))

        if db_data_set.issubset(csv_data_set):
            self.stdout.write(self.style.SUCCESS('No hay registros extra en la base de datos que no estén en el CSV.'))
        else:
            extra_in_db = db_data_set - csv_data_set
            self.stdout.write(self.style.ERROR(f'Registros en la base de datos que no están en el CSV: {extra_in_db}'))
