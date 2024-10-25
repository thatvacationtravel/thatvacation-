import csv
from tqdm import tqdm
from django.core.management.base import BaseCommand
from reservas.models import CruiseDiscount

class Command(BaseCommand):
    help = 'Load club discounts from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to load')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        discounts = []

        # Eliminar todos los datos existentes en la tabla ClubDiscount
        self.stdout.write('Deleting all existing club discounts...')
        CruiseDiscount.objects.all().delete()
        self.stdout.write('All existing club discounts have been deleted.')

        # Try opening the file with different encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1']
        for enc in encodings:
            try:
                with open(csv_file, 'r', encoding=enc) as f:
                    total_rows = sum(1 for row in f)
                break
            except UnicodeDecodeError:
                continue
        else:
            self.stderr.write(self.style.ERROR('Unable to open the file with any of the given encodings'))
            return

        with open(csv_file, newline='', encoding=enc) as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip the header row
            for row in tqdm(reader, total=total_rows, desc="Loading club discounts"):
                try:
                    discount = CruiseDiscount(
                        pax_type_cd=row[0],
                        pax_type_desc=row[1],
                        club_card=row[2] if row[2] else None,
                        disc_cd=row[3],
                        disc_desc=row[4],
                        disc_class=row[5],
                        cruise_limit=row[6],
                        cruise_id=row[7],
                        disc_rate_type=row[8],
                        disc_rate_amt=float(row[9]) if row[9].replace('.', '', 1).isdigit() else 0.0,
                        invtd=row[10] if row[10] else None,
                        min_num_a=int(row[11]) if row[11].isdigit() else None,
                        max_num_a=int(row[12]) if row[12].isdigit() else None,
                        oper_a=row[13] if row[13] else None,
                        age_a=row[14] if row[14] else None,
                        min_num_c=int(row[15]) if row[15].isdigit() else None,
                        max_num_c=int(row[16]) if row[16].isdigit() else None,
                        oper_c=row[17] if row[17] else None,
                        age_c=row[18] if row[18] else None,
                        disc_pos_a=row[19] if row[19] else None,
                        disc_pos_c=row[20] if row[20] else None,
                        combl=row[21] if len(row) > 21 else None
                    )
                    discounts.append(discount)
                except ValueError as e:
                    self.stderr.write(self.style.ERROR(f'Error processing row {row}: {e}'))
                    continue

                # Bulk create every 1000 items to avoid memory issues
                if len(discounts) % 1000 == 0:
                    CruiseDiscount.objects.bulk_create(discounts)
                    discounts = []

        # Create remaining items
        if discounts:
            CruiseDiscount.objects.bulk_create(discounts)

        self.stdout.write(self.style.SUCCESS('Club discounts have been successfully loaded'))
