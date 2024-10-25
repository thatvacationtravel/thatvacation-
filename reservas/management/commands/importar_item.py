from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from reservas.models import Item
import json
import os
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Importa detalles de items desde archivos JSON divididos a la base de datos sin eliminar los datos existentes'

    def add_arguments(self, parser):
        parser.add_argument('json_dir_path', type=str, help='Ruta del directorio con los archivos JSON divididos')

    def handle(self, *args, **kwargs):
        dir_path = kwargs['json_dir_path']
        error_log_path = os.path.join(dir_path, "error_log.txt")

        # Inicializar el archivo de registro de errores
        if os.path.exists(error_log_path):
            os.remove(error_log_path)

        json_files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
        total_item_count = 0

        for json_file in json_files:
            self.stdout.write(self.style.SUCCESS(f'Procesando archivo: {json_file}'))
            file_path = os.path.join(dir_path, json_file)
            to_create = []
            batch_size = 800
            item_count = 0

            with open(file_path, 'r', encoding='utf-8') as jsonfile, open(error_log_path, 'a', encoding='utf-8') as error_log:
                try:
                    data = json.load(jsonfile)
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f'Error decodificando JSON en archivo {json_file}: {e}'))
                    continue
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error leyendo el archivo JSON {json_file}: {e}'))
                    continue

                for row in tqdm(data, desc=f"Procesando registros del JSON {json_file}"):
                    try:
                        # Convertir tipos de datos de string a adecuados
                        price_infant = float(row.get('priceInfant', '0'))
                        price_jr_child = float(row.get('priceJrChild', '0'))
                        price_child = float(row.get('priceChild', '0'))
                        price_adult = float(row.get('priceAdult', '0'))
                        price_senior = float(row.get('priceSenior', '0'))
                        start_dt = parse_date(row.get('startDt')) if row.get('startDt') else None
                        end_dt = parse_date(row.get('endDt')) if row.get('endDt') else None

                        new_item = Item(
                            item_type_code=row['itemTypeCode'],
                            item_code=row['itemCode'],
                            fare_code=row['fareCode'],
                            category=row['category'],
                            price_type=row.get('priceType'),
                            price_basis=row.get('priceBasis'),
                            pax_applicability=row.get('paxApplicability'),
                            price_infant=price_infant,
                            price_jr_child=price_jr_child,
                            price_child=price_child,
                            price_adult=price_adult,
                            price_senior=price_senior,
                            item_description=row.get('itemDescription'),
                            item_description_long=row.get('itemDescriptionLong'),
                            service_type=row.get('serviceType'),
                            service_type_desc=row.get('serviceTypeDesc'),
                            package_code=row.get('packageCode'),
                            loc_cd=row.get('locCd'),
                            port_cd=row.get('portCd'),
                            start_dt=start_dt,
                            end_dt=end_dt,
                            ship_cd=row.get('shipCd'),
                            inventoried=row.get('inventoried'),
                            apply_to=row.get('applyTo', 'default_value'),  # Asignar valor predeterminado
                            reg_cd=row.get('regCd', 'default_reg_cd'),
                            pax_type=row.get('paxType', 'default_pax_type')
                        )
                        to_create.append(new_item)
                        item_count += 1
                        total_item_count += 1

                        if len(to_create) >= batch_size:
                            Item.objects.bulk_create(to_create)
                            self.stdout.write(self.style.SUCCESS(f'{len(to_create)} registros insertados.'))
                            to_create.clear()
                    except Exception as e:
                        error_log.write(f'Error procesando registro en archivo {json_file}: {row}\n{e}\n')

                if to_create:
                    Item.objects.bulk_create(to_create)
                    self.stdout.write(self.style.SUCCESS(f'{len(to_create)} registros insertados.'))

            self.stdout.write(self.style.SUCCESS(f'Total de registros insertados desde {json_file}: {item_count}'))

        self.stdout.write(self.style.SUCCESS(f'Total de registros insertados: {total_item_count}'))
