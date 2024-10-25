import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime
from decimal import Decimal, InvalidOperation
from reservas.models import Cruise
import time
import traceback

class Command(BaseCommand):
    help = 'Sincroniza registros de cruceros entre la base de datos y un archivo CSV.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', type=str, help='Ruta al archivo CSV con datos de cruceros.')

    def handle(self, *args, **kwargs):
        start_time = time.time()
        csv_file_path = kwargs['csv_file_path']

        try:
            csv_cruise_ids = set()
            total_csv_records = 0  # Contador de registros en el CSV
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    csv_cruise_ids.add((row['CRUISE-ID'], row.get('FARE-CD')))
                    total_csv_records += 1  # Incrementar el contador por cada fila procesada

            total_deleted = self.delete_missing_cruises(csv_cruise_ids)

            if total_deleted == 0:
                existing_cruise_ids = {(cruise[0], cruise[1]) for cruise in Cruise.objects.values_list('cruiseID', 'fareCode')}
                if existing_cruise_ids == csv_cruise_ids:
                    self.stdout.write(self.style.SUCCESS('No hay discrepancias entre la base de datos y el CSV. No se requiere ninguna actualización.'))
                    self.stdout.write(self.style.SUCCESS(f'Total de cruceros en la base de datos: {Cruise.objects.count()}'))
                    self.stdout.write(self.style.SUCCESS(f'Total de registros en el CSV: {total_csv_records}'))
                    self.stdout.write(self.style.SUCCESS(f'Tiempo de ejecución total: {time.time() - start_time:.2f} segundos'))
                    return

            # Segunda instancia: Insertar nuevos registros desde el CSV procesado por lotes
            total_added = self.add_new_cruises(csv_file_path, csv_cruise_ids)

            # Detalles finales
            total_db_objects = Cruise.objects.count()  # Contar objetos en la BD tras la sincronización
            self.stdout.write(self.style.SUCCESS(f'Total de cruceros en la base de datos después de la sincronización: {total_db_objects}'))
            self.stdout.write(self.style.SUCCESS(f'Total de cruceros eliminados: {total_deleted}'))
            self.stdout.write(self.style.SUCCESS(f'Total de cruceros agregados: {total_added}'))
            self.stdout.write(self.style.SUCCESS(f'Total de registros en el CSV: {total_csv_records}'))
            self.stdout.write(self.style.SUCCESS(f'Tiempo de ejecución total: {time.time() - start_time:.2f} segundos'))
            self.stdout.write(self.style.SUCCESS('La sincronización se realizó exitosamente.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error durante la sincronización: {str(e)}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def delete_missing_cruises(self, csv_cruise_ids):
        """
        Elimina los cruceros de la base de datos cuyos cruiseID y fareCode no coinciden con ningún objeto del CSV.
        """
        total_deleted = 0
        with transaction.atomic():
            # Utiliza values_list para obtener solo los campos necesarios
            existing_cruises = Cruise.objects.values_list('id', 'cruiseID', 'fareCode')
            to_delete = [cruise[0] for cruise in existing_cruises if (cruise[1], cruise[2]) not in csv_cruise_ids]
            total_deleted = len(to_delete)
            if to_delete:
                Cruise.objects.filter(id__in=to_delete).delete()

        return total_deleted

    def add_new_cruises(self, csv_file_path, csv_cruise_ids):
        """
        Inserta nuevos cruceros que no existan en la base de datos basados en cruiseID y fareCode.
        """
        new_cruises = []
        total_added = 0
        BATCH_SIZE = 1000  

        existing_cruise_ids = {(cruise[0], cruise[1]) for cruise in Cruise.objects.values_list('cruiseID', 'fareCode')}

        with transaction.atomic():
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=';')
                for row in reader:
                    cruise_tuple = (row['CRUISE-ID'], row.get('FARE-CD'))
                    if cruise_tuple not in existing_cruise_ids:
                        new_cruise = self.create_cruise_from_row(row)
                        new_cruises.append(new_cruise)

                    # Insertar en lotes cuando se alcanza el tamaño
                    if len(new_cruises) >= BATCH_SIZE:
                        Cruise.objects.bulk_create(new_cruises)
                        total_added += len(new_cruises)
                        new_cruises = []  # Reiniciar la lista para el siguiente lote

                # Insertar cualquier resto que quede
                if new_cruises:
                    Cruise.objects.bulk_create(new_cruises)
                    total_added += len(new_cruises)

        return total_added

    def create_cruise_from_row(self, row):
        return Cruise(
            cruiseID=row['CRUISE-ID'],
            shipCd=row['SHIP-CD'],
            sailingPort=row['SAILING-PORT'],
            terminationPort=row.get('TERMINATION-PORT', ''),
            shipName=row.get('SHIP-NAME', ''),
            sailingDate=self.parse_date(row.get('SAILING-DATE')),
            nights=row.get('NIGHTS', 0),
            itinCd=row.get('ITIN-CD', ''),
            itinDesc=row.get('ITIN-DESC', ''),
            fareCode=row.get('FARE-CD', ''),
            fareDesc=row.get('FARE-DESC', ''),
            items=row.get('ITEMS', ''),
            category=row.get('CATEGORY', ''),
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
            ncfA=self.parse_decimal(row.get('NCF-A')),
            ncfC=self.parse_decimal(row.get('NCF-C')),
            ncfJ=self.parse_decimal(row.get('NCF-J')),
            gftA=self.parse_decimal(row.get('GFT-A')),
            gftC=self.parse_decimal(row.get('GFT-C')),
            embkTime=row.get('SAIL-TIME-EMBK', ''),
            disEmbkTime=row.get('SAIL-TIME-DISMBK', ''),
            cruiseOnly=row.get('CRUISE-ONLY', '') == 'YES',
            nowAvailable=row.get('NOW-AVAIL', '') == 'YES',
            clubDiscount=row.get('CLUB-DISCOUNT', '') == 'YES',
            flightStatus=row.get('FLIGHT-STATUS', ''),
            flightPriceType=row.get('FLIGHT-PRICE-TYPE', ''),
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
        if value in ['N/A', '', None]:
            return None
        try:
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
