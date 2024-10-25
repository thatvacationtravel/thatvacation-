import csv
from tqdm import tqdm  # Importa tqdm
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from datetime import datetime
from decimal import Decimal, InvalidOperation
from reservas.models import Cruise

class Command(BaseCommand):
    help = 'Reemplaza todos los registros de cruceros en la base de datos con los del archivo CSV y muestra el progreso.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta al archivo CSV con datos de cruceros.')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file_path']

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            data = [row for row in reader if row.get('NOW-AVAIL') == 'YES']  # Filtra solo los disponibles
            total_rows = len(data)

        if total_rows == 0:
            self.stdout.write(self.style.WARNING('No hay cruceros disponibles para importar.'))
            return

        try:
            with transaction.atomic():
                # Truncar la tabla Cruise
                with connection.cursor() as cursor:
                    cursor.execute('TRUNCATE TABLE reservas_cruise;')
                self.stdout.write(self.style.SUCCESS('Todos los datos han sido eliminados de la tabla cruise.'))

                cruises = []
                
                # Usar tqdm para mostrar el progreso
                for row in tqdm(data, desc="Importando cruceros", unit="crucero"):
                    cruise = self.create_cruise_from_row(row)
                    cruises.append(cruise)

                # Importar todos los cruceros de una vez
                Cruise.objects.bulk_create(cruises, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'\n{len(cruises)} cruceros han sido importados exitosamente.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la importación: {e}'))
            import logging
            logger = logging.getLogger(__name__)
            logger.error('Error durante la importación', exc_info=True)

    def create_cruise_from_row(self, row):
        return Cruise(
            cruiseID=row['CRUISE-ID'],
            shipCd=row['SHIP-CD'],
            sailingPort=row['SAILING-PORT'],
            terminationPort=row['TERMINATION-PORT'],
            shipName=row['SHIP-NAME'],
            sailingDate=self.parse_date(row.get('SAILING-DATE')),
            nights=row['NIGHTS'],
            itinCd=row['ITIN-CD'],
            itinDesc=row['ITIN-DESC'],
            fareCode=row['FARE-CD'],
            fareDesc=row['FARE-DESC'],
            items=row['ITEMS'],
            category=row['CATEGORY'],
            oneAdult=self.parse_decimal(row.get('1A')),
            twoAdult=self.parse_decimal(row.get('2A')),
            threeAdult=self.parse_decimal(row.get('3A')),
            fourAdult=self.parse_decimal(row.get('4A')),
            twoAdult1Ch=self.parse_decimal(row.get('2A1C')),
            twoAdult2Ch=self.parse_decimal(row.get('2A2C')),
            oneAdult1Ch=self.parse_decimal(row.get('1A1C')),
            oneAdult1JrCh=self.parse_decimal(row.get('1A1J')),
            twoAdult1JrCh=self.parse_decimal(row.get('2A1J')),
            twoAdult1Ch1JrCh=self.parse_decimal(row.get('2A1C1J')),
            twoAdult2JrCh=self.parse_decimal(row.get('2A2J')),
            ncfA=self.parse_decimal(row['NCF-A']),
            ncfC=self.parse_decimal(row['NCF-C']),
            ncfJ=self.parse_decimal(row['NCF-J']),
            gftA=self.parse_decimal(row.get('GFT-A')),
            gftC=self.parse_decimal(row.get('GFT-C')),
            embkTime=row['SAIL-TIME-EMBK'],
            disEmbkTime=row['SAIL-TIME-DISMBK'],
            cruiseOnly=row['CRUISE-ONLY'] == 'YES',
            nowAvailable=row['NOW-AVAIL'] == 'YES',
            clubDiscount=row['CLUB-DISCOUNT'] == 'YES',
            flightStatus=row['FLIGHT-STATUS'],
            flightPriceType=row['FLIGHT-PRICE-TYPE'],
            fareStartDate=self.parse_date(row.get('FARE-START-DT')),
            fareEndDate=self.parse_date(row.get('FARE-END-DT')),
            fareStartTime=row.get('FARE-START-TIM', ''),
            fareEndTime=row.get('FARE-END-TIM', ''),
            optionExpiresDate=self.parse_date(row.get('OPTION-EXPIRES-DATE')),
            lmtOrgApt=row.get("ROUTING-OUT", ""),
            defaultPorts=row.get("ROUTING-RET", ""),
            irCoef=row.get("AIR-COST-A", ""),
            ppdA=row.get("AIR-COST-C", ""),
            ppdJc=row.get("AIR-COST-I", ""),
            ppdPriceType=row.get("PRICE-TYPE", ""),
            ppdPriceBasis=row.get("PRICE-BASIS", ""),
            ppdApplyAs=row.get("APPLY-AS", ""),
            serviceChargeCode=row.get("SERV-CHARGE-CD", ""),
            serviceChargeSenior=row.get("SERV-CHARGE-S", ""),
            serviceChargeAdult=row.get("SERV-CHARGE-A", ""),
            serviceChargeChild=row.get("SERV-CHARGE-C", ""),
            serviceChargeJunior=row.get("SERV-CHARGE-J", ""),
            serviceChargeInfant=row.get("SERV-CHARGE-I", "")
        )

    def parse_decimal(self, value):
        try:
            if value in ['N/A', '', None]:
                return None
            return Decimal(value.replace(',', '.'))
        except InvalidOperation:
            return None

    def parse_date(self, date_str, date_format='%d/%m/%Y'):
        if date_str in ['N/A', '', None]:
            return None
        try:
            return datetime.strptime(date_str, date_format).date()
        except ValueError:
            return None
