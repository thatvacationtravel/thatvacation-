import csv
import os
from django.core.management.base import BaseCommand
from tqdm import tqdm
from reservas.models import State 

class Command(BaseCommand):
    help = 'Importa los detalles de los estados '

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta del archivo CSV')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file_path']
        error_log_path = os.path.join(os.path.dirname(file_path), "error_log.txt")

        if os.path.exists(error_log_path):
            os.remove(error_log_path)

        to_create = []
        batch_size = 1000
        total_state_count = 0

        with open(file_path, 'r', encoding='utf-8') as csvfile, open(error_log_path, 'a', encoding='utf-8') as error_log:
            reader = csv.DictReader(csvfile)

            for row in tqdm(reader, desc=f"Procesando registros del CSV {os.path.basename(file_path)}"):
                try:
                    code = row['CODE'].strip()
                    name = row['NAME'].strip()

                    # Crear o actualizar el estado en la base de datos
                    new_state, created = State.objects.update_or_create(
                        code=code,
                        defaults={'name': name}
                    )
                    total_state_count += 1

                except Exception as e:
                    error_log.write(f'Error procesando registro: {row}\n{e}\n')
                    self.stdout.write(self.style.WARNING(f'Error en fila: {row}\n{e}\n'))

        self.stdout.write(self.style.SUCCESS(f'Total de registros insertados: {total_state_count}'))
