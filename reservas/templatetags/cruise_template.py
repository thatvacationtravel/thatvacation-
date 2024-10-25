from datetime import date
from django.http import HttpResponse

cruise_date= date(2025, 2, 14)

def check_cruise():
    current_date = date.today()
    if current_date >= cruise_date:
        return True
    return False

def cruise_msc():
    pass