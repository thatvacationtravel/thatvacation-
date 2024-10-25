from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from reservas.models import Item
import csv
import os
from tqdm import tqdm
from django.db import transaction

class Command(BaseCommand):
    help = 'Sincroniza los items entre la base de datos y el archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file_path']
        error_log_path = os.path.join(os.path.dirname(file_path), "error_log.txt")

        if os.path.exists(error_log_path):
            os.remove(error_log_path)

        csv_item_ids = self.extract_csv_items(file_path)
        total_deleted = self.delete_missing_items(csv_item_ids)

        total_inserted = self.insert_new_items(file_path, csv_item_ids)
        total_db_objects = Item.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total de registros en la base de datos después de la sincronización: {total_db_objects}'))
        self.stdout.write(self.style.SUCCESS(f'Total de registros eliminados: {total_deleted}'))
        self.stdout.write(self.style.SUCCESS(f'Total de registros insertados: {total_inserted}'))

    def extract_csv_items(self, file_path):
        csv_item_ids = set()
        with open(file_path, 'r', encoding='ISO-8859-1') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in tqdm(reader, desc="Extrayendo identificadores del CSV"):
                if len(row) == 15:
                    fare_code = row[2].strip()
                    item_code = row[1].strip()
                    package_code = row[14].strip()
                    csv_item_ids.add((fare_code, item_code, package_code))
        return csv_item_ids

    def delete_missing_items(self, csv_item_ids):

        total_deleted = 0
        with transaction.atomic():
            existing_items = Item.objects.values_list('id', 'fare_code', 'item_code', 'package_code')
            to_delete = [item[0] for item in existing_items if (item[1], item[2], item[3]) not in csv_item_ids]
            total_deleted = len(to_delete)
            if to_delete:
                Item.objects.filter(id__in=to_delete).delete()
        return total_deleted

    def insert_new_items(self, file_path, csv_item_ids):

        to_create = []
        batch_size = 500
        total_inserted = 0

        existing_items = set(Item.objects.values_list('fare_code', 'item_code', 'package_code'))

        with open(file_path, 'r', encoding='ISO-8859-1') as csvfile, open(os.path.join(os.path.dirname(file_path), "error_log.txt"), 'a', encoding='utf-8') as error_log:
            for line in tqdm(csvfile, desc="Procesando registros del CSV para inserción"):
                try:
                    row = self.custom_split(line.strip())

                    fare_code = row[2].strip()
                    item_code = row[1].strip()
                    package_code = row[14].strip()

                    if (fare_code, item_code, package_code) not in existing_items:
                        price_infant = float(row[7])
                        price_jr_child = float(row[8])
                        price_child = float(row[9])
                        price_adult = float(row[10])
                        price_senior = float(row[11])
                        start_dt = parse_date(row[14]) if row[14] else None
                        end_dt = parse_date(row[14]) if row[14] else None

                        new_item = Item(
                            item_type_code=row[0],
                            item_code=item_code,
                            fare_code=fare_code,
                            category=row[3],
                            price_type=row[4],
                            price_basis=row[5],
                            pax_applicability=row[6],
                            price_infant=price_infant,
                            price_jr_child=price_jr_child,
                            price_child=price_child,
                            price_adult=price_adult,
                            price_senior=price_senior,
                            item_description=row[12],
                            item_description_long=row[13],
                            service_type=row[6],
                            package_code=package_code
                        )
                        to_create.append(new_item)
                        total_inserted += 1

                        if len(to_create) >= batch_size:
                            Item.objects.bulk_create(to_create)
                            to_create.clear()
                except Exception as e:
                    error_log.write(f'Error procesando registro: {line}\n{e}\n')

            if to_create:
                Item.objects.bulk_create(to_create)

        return total_inserted

    def custom_split(self, line):

        fields = []
        current_field = []
        i = 0
        while i < len(line):
            if line[i] == ';':
                if i + 1 < len(line) and line[i + 1] != ' ':
                    fields.append(''.join(current_field).strip())
                    current_field = []
                else:
                    current_field.append(line[i])
            else:
                current_field.append(line[i])
            i += 1
        fields.append(''.join(current_field).strip())
        return fields
