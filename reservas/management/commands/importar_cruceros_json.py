import json
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from decimal import Decimal, InvalidOperation
from reservas.models import Cruise

class Command(BaseCommand):
    help = 'Reemplaza todos los registros de cruceros en la base de datos con los del archivo JSON y muestra el progreso.'

    def add_arguments(self, parser):
        parser.add_argument('json_file_path', type=str, help='Ruta al archivo JSON con datos de cruceros.')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file_path']
        with open(json_file_path, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            total_rows = len(data)

        try:
            with transaction.atomic():
                Cruise.objects.all().delete()  # Eliminar todos los registros existentes
                cruises = []
                processed_rows = 0
                print_interval = 1000  # Imprime el progreso cada 1000 filas procesadas

                for row in data:
                    cruise = self.create_cruise_from_row(row)
                    cruises.append(cruise)
                    processed_rows += 1

                    # Imprime solo cada 1000 filas para limitar la salida
                    if processed_rows % print_interval == 0:
                        self.stdout.write(self.style.SUCCESS(f'Procesado {processed_rows} de {total_rows} registros.'), ending='\r')

                # Asegúrate de imprimir el progreso final si no es múltiplo de print_interval
                if processed_rows % print_interval != 0:
                    self.stdout.write(self.style.SUCCESS(f'Procesado {processed_rows} de {total_rows} registros.'), ending='\r')

                Cruise.objects.bulk_create(cruises, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'\n{len(cruises)} cruceros han sido importados exitosamente.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la importación: {e}'))
            # Considera también usar logging para registrar el error
            import logging
            logger = logging.getLogger(__name__)
            logger.error('Error durante la importación', exc_info=True)

    def create_cruise_from_row(self, row):
        # Aquí asignas cada campo del JSON a los campos del modelo Cruise
        return Cruise(
            cruiseID=row['cruiseID'],
            shipCd=row['shipCd'],
            sailingPort=row['sailingPort'],
            terminationPort=row['terminationPort'],
            shipName=row['shipName'],
            sailingDate=self.parse_date(row.get('sailingDate')),
            nights=row['nights'],
            itinCd=row['itinCd'],
            itinDesc=row['itinDesc'],
            fareCode=row['fareCode'],
            fareDesc=row['fareDesc'],
            items=row['items'],
            category=row['category'],
            priceType=row['priceType'],
            oneAdult=self.parse_decimal(row.get('oneAdult')),
            twoAdult=self.parse_decimal(row.get('twoAdult')),
            threeAdult=self.parse_decimal(row.get('threeAdult')),
            fourAdult=self.parse_decimal(row.get('fourAdult')),
            twoAdult1Ch=self.parse_decimal(row.get('twoAdult1Ch')),
            twoAdult2Ch=self.parse_decimal(row.get('twoAdult2Ch')),
            oneAdult1Ch=self.parse_decimal(row.get('oneAdult1Ch')),
            oneAdult1JrCh=self.parse_decimal(row.get('oneAdult1JrCh')),
            twoAdult1JrCh=self.parse_decimal(row.get('twoAdult1JrCh')),
            twoAdult1Ch1JrCh=self.parse_decimal(row.get('twoAdult1Ch1JrCh')),
            twoAdult2JrCh=self.parse_decimal(row.get('twoAdult2JrChA')),
            ncfA=self.parse_decimal(row['ncfA']),
            ncfC=self.parse_decimal(row['ncfC']),
            ncfJ=self.parse_decimal(row['ncfJ']),
            gftA=self.parse_decimal(row.get('gftA')),
            gftC=self.parse_decimal(row.get('gftC')),
            embkTime=row['embkTime'],
            disEmbkTime=row['disEmbkTime'],
            cruiseOnly=row['cruiseOnly'] == 'YES',
            nowAvailable=row['nowAvailable'] == 'YES',
            clubDiscount=row['clubDiscount'] == 'YES',
            flightStatus=row['flightStatus'],
            flightPriceType=row['flightPriceType'],
            fareStartDate=self.parse_date(row.get('fareStartDate')),
            fareEndDate=self.parse_date(row.get('fareEndDate')),
            fareStartTime=row.get('fareStartTime', ''),
            fareEndTime=row.get('fareEndTime', ''),
            optionExpiresDate=self.parse_date(row.get('optionExpiresDate')),
            lmtOrgApt=row.get("routingOut", ""),
            defaultPorts=row.get("routingReturn", ""),
            irCoef=row.get("irCoef", ""),
            ppdA=row.get("ppdA", ""),
            ppdJc=row.get("ppdJc", ""),
            ppdPriceType=row.get("ppdPriceType", ""),
            ppdPriceBasis=row.get("ppdPriceBasis", ""),
            ppdApplyAs=row.get("ppdApplyAs", ""),
            serviceChargeCode=row.get("serviceChargeCode", ""),
            serviceChargeSenior=row.get("serviceChargeSenior", ""),
            serviceChargeAdult=row.get("serviceChargeAdult", ""),
            serviceChargeChild=row.get("serviceChargeChild", ""),
            serviceChargeJunior=row.get("serviceChargeJunior", ""),
            serviceChargeInfant=row.get("serviceChargeInfant", "")
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
