import csv
from django.core.management.base import BaseCommand
from tqdm import tqdm
from reservas.models import Categories

class Command(BaseCommand):
    help = 'Importa y actualiza registros desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV con los datos de los registros')

    def handle(self, *args, **kwargs):
        path = kwargs['csv_file_path']
        Categories.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Todos los registros han sido eliminados.'))

        registros_para_crear = []

        with open(path, newline='', encoding='ISO-8859-1') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            total_registros = sum(1 for row in reader)  # Contar el total de registros en el archivo
            csvfile.seek(0)  # Reiniciar el cursor del archivo para volver a leerlo
            next(reader)  # Omitir la fila de encabezados

            for row in tqdm(reader, total=total_registros, desc='Importando registros'):
                nuevo_registro = Categories(
                    tipo=row['TYPE'],
                    codigo=row['CODE'],
                    fare_cd=row['FARE-CD'],
                    categoria=row['CATEGORY'],
                    apply_type=row['APPLY-TYPE'],
                    apply_method=row['APPLY-METHOD'],
                    apply_pax=row['APPLY-PAX'],
                    price_i=float(row['PRICE-I']),
                    price_j=float(row['PRICE-J']),
                    price_c=float(row['PRICE-C']),
                    price_a=float(row['PRICE-A']),
                    price_s=float(row['PRICE-S']),
                    descripcion=row['DESC'],
                    descripcion_larga=row['DESC-LONG'],
                    package_code=row['PACKAGE_CODE']
                )
                registros_para_crear.append(nuevo_registro)

        # Crear registros en lotes
        batch_size = 1000
        for i in range(0, len(registros_para_crear), batch_size):
            Categories.objects.bulk_create(registros_para_crear[i:i+batch_size])

        self.stdout.write(self.style.SUCCESS('Todos los registros han sido importados correctamente.'))
