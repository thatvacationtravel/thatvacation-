from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from reservas.models import Item
import csv
import os
from tqdm import tqdm
import re

class Command(BaseCommand):
    help = 'Importa detalles de items desde un archivo CSV a la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file_path']
        error_log_path = os.path.join(os.path.dirname(file_path), "error_log.txt")

        # Inicializar el archivo de registro de errores
        if os.path.exists(error_log_path):
            os.remove(error_log_path)

        to_create = []
        batch_size = 500
        item_count = 0
        total_item_count = 0

        with open(file_path, 'r', encoding='ISO-8859-1') as csvfile, open(error_log_path, 'a', encoding='utf-8') as error_log:
            for line in tqdm(csvfile, desc=f"Procesando registros del CSV {os.path.basename(file_path)}"):
                try:
                    # Procesar la línea utilizando la lógica de delimitadores personalizada
                    row = self.custom_split(line.strip())

                    # Verificar que la fila tenga la cantidad correcta de campos
                    if len(row) != 15:
                        raise ValueError(f"Número incorrecto de campos: {len(row)} esperados 15")

                    # Convertir tipos de datos de string a adecuados
                    price_infant = float(row[7])
                    price_jr_child = float(row[8])
                    price_child = float(row[9])
                    price_adult = float(row[10])
                    price_senior = float(row[11])
                    start_dt = parse_date(row[14]) if row[14] else None
                    end_dt = parse_date(row[14]) if row[14] else None

                    new_item = Item(
                        item_type_code=row[0],
                        item_code=row[1],
                        fare_code=row[2],
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
                        service_type=row[6],  # No hay servicio específico en los datos originales
                        package_code=row[14]
                    )
                    to_create.append(new_item)
                    item_count += 1
                    total_item_count += 1

                    if len(to_create) >= batch_size:
                        Item.objects.bulk_create(to_create)
                        self.stdout.write(self.style.SUCCESS(f'{len(to_create)} registros insertados en el batch.'))
                        to_create.clear()
                except Exception as e:
                    error_log.write(f'Error procesando registro: {line}\n{e}\n')
                    # Mensaje de depuración adicional
                    self.stdout.write(self.style.WARNING(f'Error en fila: {line}\n{e}\n'))

            if to_create:
                Item.objects.bulk_create(to_create)
                self.stdout.write(self.style.SUCCESS(f'{len(to_create)} registros insertados en el batch final.'))

        self.stdout.write(self.style.SUCCESS(f'Total de registros insertados: {total_item_count}'))

    def custom_split(self, line):
        """
        Divide una línea basada en el delimitador ; sin espacios siguientes, manejando correctamente campos complejos.
        """
        fields = []
        current_field = []
        i = 0
        while i < len(line):
            if line[i] == ';':
                if i + 1 < len(line) and line[i + 1] != ' ':
                    # Encontramos un delimitador
                    fields.append(''.join(current_field).strip())
                    current_field = []
                else:
                    # Parte del contenido del campo
                    current_field.append(line[i])
            else:
                current_field.append(line[i])
            i += 1
        # Añadir el último campo
        fields.append(''.join(current_field).strip())
        return fields
