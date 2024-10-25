import json
from datetime import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import os
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thatvacation.settings')
django.setup()

from reservas.models import Cruise


def convert_decimal(value):
    if value is None or value == "N/A":
        return None

    parts = value.split("|")
    decimal_values = []
    for part in parts:
        try:
            decimal_value = Decimal(part)
            decimal_values.append(decimal_value)
        except:
            pass
    if decimal_values:
        return decimal_values
    else:
        return None


def convert_gft(value):
    value = value.replace(',', '.')
    try:
        decimal_value = Decimal(value)
        return decimal_value
    except:
        return None



def convert_date(date_string):
    return datetime.strptime(date_string, '%d/%m/%Y').date() if date_string else None

class Command(BaseCommand):
    help = 'Importar los datos de cruceros desde el JSON'

    def handle(self, *args, **options):
        json_file_path = '/home/tvacation/thatvacation/json/flatfile_usa_air.json'

        with open(json_file_path, 'r') as file:
            data = json.load(file)
            for item in data:
                try:
                    items = convert_decimal(item['items'])
                    sailing_date = convert_date(item['sailingDate'])
                    fare_start_date = convert_date(item['fareStartDate'])
                    fare_end_date = convert_date(item['fareEndDate'])
                    fare_start_time = convert_date(item.get('fareStartTime'))
                    option_expires_date = convert_date(item.get('optionExpiresDate'))

                    lmtOrgApt_value = item['lmtOrgApt']
                    if lmtOrgApt_value == "N/A":
                        lmtOrgApt_value = None

                    cruise, created = Cruise.objects.update_or_create(
                        cruiseID=item['cruiseID'],
                        defaults={
                            'shipCd': item['shipCd'],
                            'sailingPort': item['sailingPort'],
                            'terminationPort': item['terminationPort'],
                            'shipName': item['shipName'],
                            'sailingDate': sailing_date,
                            'nights': item['nights'],
                            'itinCd': item['itinCd'],
                            'itinDesc': item['itinDesc'],
                            'fareCode': item['fareCode'],
                            'category': item['category'],
                            'fareDesc': item['fareDesc'],
                            'items': items,
                            'priceType': item['priceType'],
                            'oneAdult': item['oneAdult'],
                            'twoAdult': item['twoAdult'],
                            'threeAdult': item['threeAdult'],
                            'fourAdult': item['fourAdult'],
                            'twoAdult1Ch': item['twoAdult1Ch'],
                            'twoAdult2Ch': item['twoAdult2Ch'],
                            'oneAdult1Ch': item['oneAdult1Ch'],
                            'oneAdult1JrCh': item['oneAdult1JrCh'],
                            'twoAdult1JrCh': item['twoAdult1JrCh'],
                            'twoAdult1Ch1JrCh': item['twoAdult1Ch1JrCh'],
                            'twoAdult2JrCh': item['twoAdult2JrCh'],
                            'ncfA': item['ncfA'],
                            'ncfC': item['ncfC'],
                            'ncfJ': item['ncfJ'],
                            'gftA': Decimal(item['gftA'].replace(',', '.')),
                            'gftC': Decimal(item['gftC'].replace(',', '.')),
                            'embkTime': item['embkTime'],
                            'disEmbkTime': item['disEmbkTime'],
                            'cruiseOnly': item['cruiseOnly'] == 'YES',
                            'nowAvailable': item['nowAvailable'] == 'YES',
                            'clubDiscount': item['clubDiscount'] == 'YES',
                            'flightStatus': item['flightStatus'],
                            'flightPriceType': item['flightPriceType'],
                            'fareStartDate': fare_start_date,
                            'fareStartTime': fare_start_time,
                            'fareEndDate': fare_end_date,
                            'optionExpiresDate': option_expires_date,
                            'lmtOrgApt': lmtOrgApt_value,
                            'defaultPorts': item.get('defaultPorts'),
                            'irCoef': item.get('irCoef'),
                            'ppdA': item['ppdA'],
                            'ppdJc': item['ppdJc'],
                            'ppdPriceType': item['ppdPriceType'],
                            'ppdPriceBasis': item['ppdPriceBasis'],
                            'ppdApplyAs': item['ppdApplyAs'],
                            'serviceChargeCode': item['serviceChargeCode'],
                            'serviceChargeSenior': item['serviceChargeSenior'],
                            'serviceChargeAdult': item['serviceChargeAdult'],
                            'serviceChargeChild': item['serviceChargeChild'],
                            'serviceChargeJunior': item['serviceChargeJunior'],
                            'serviceChargeInfant': item['serviceChargeInfant'],
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Successfully created cruise {cruise.cruiseID}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Updated cruise {cruise.cruiseID}'))
                except IntegrityError as e:
                    self.stdout.write(self.style.ERROR(f'Error de integridad en {item["cruiseID"]}: {e}'))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Error de validación en {item["cruiseID"]}: {e}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error inesperado en {item["cruiseID"]}: {e}'))
