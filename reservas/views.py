from django.shortcuts import render, redirect
import os
from django.template import loader
from django.contrib.auth import login as do_login, authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from reservas.forms import UCFWithEmail,UserProfileForm, HotelSearchForm, DinigForm, CustomUserLoginForm, CommentForm, CruiseSearchForm1
from django.contrib import auth
from reservas.models import comentarios, State, Cancelations, Employed, Categories, Item, cabinDetail, InvoiceCustomer, Itinerary, Cabin, destino, paqueteoferta, Cruise, CruiseSearch, City, Port, Booking
from reservas.templatetags.cruise_template import cruise_msc, check_cruise
from django.contrib.auth import get_user_model
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse
import xml.dom.minidom
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
import requests
import xml.etree.ElementTree as ET
from lxml import etree
import decimal
from django.views import View
from django.urls import reverse, NoReverseMatch
import re
decimal.getcontext().prec = 6
from decimal import Decimal
from django.contrib.auth.decorators import user_passes_test
import hashlib
from emailapp.models import template_email
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import HttpResponseForbidden
from datetime import timedelta
from django.http import HttpResponseRedirect
from reportlab.lib.enums import TA_JUSTIFY
from django.utils import timezone
import plotly.express as px



from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


def usuario_aprobado_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.aprobacion:
            return redirect('/error/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func




def send_email(subject, message, recipient_list, email_type='contact'):
    if email_type == 'contact':
        email_config = settings.EMAIL_CONTACT_BACKEND
    else:
        raise ValueError("Email type not recognized")

    if isinstance(email_config, dict):
        send_mail(
            subject,
            message,
            email_config['EMAIL_HOST_USER'],
            recipient_list,
            fail_silently=False,
            auth_user=email_config['EMAIL_HOST_USER'],
            auth_password=email_config['EMAIL_HOST_PASSWORD'],
        )
    else:
        raise TypeError("Email configuration is not a dictionary.")







def is_agency(user):
    return user.groups.filter(name='Agencias').exists()


def cookies_policy(request):

    return render(request, 'cookies_policy.html')

def termcondition(request):


    return render(request, "testimonial.html")

def politicprivacy(request):


    return render(request, "politicas_privacidad.html")


def pack(request):

    return render(request, "package.html")

def bestdeal(request):

    return render(request, "bestdeal.html")

def about(request):
    employed = Employed.objects.all()

    return render(request, "about.html", {'employed': employed})



def detail_employed(request, employed_id):
    employed = get_object_or_404(Employed, id=employed_id)

    return render(request, "detail_employed.html", {'employed': employed})


def donotsale(request):
    
    return render(request, "donot.html")

def services(request):

    return render(request, "service.html")


def contact(request):

    return render(request, "contact.html")


def go_back_view(request):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('nombre_de_url_predeterminada')



def index(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('myaccounts')
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = CustomUserLoginForm()

    return render(request, 'index.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                form.add_error(None, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = CustomUserLoginForm()

    return render(request, "login.html", {'form': form})


def ofertas(request, paquete_id, nombre):
    paquete = paqueteoferta.objects.get(id=paquete_id)
    ofertas = destino.objects.filter(paquete_oferta=paquete)
    return render(request, 'ofertas.html', {'ofertas': ofertas})



def register(request, backend='django.contrib.auth.backends.ModelBackend'):
    form = UCFWithEmail()
    if request.method == 'POST':
        form = UCFWithEmail(data=request.POST)
        if form.is_valid():
            user = form.save()
            if user is not None:
                send_registration_email(user.email, 'thatvacationtravel@gmail.com')
                if user.is_active:
                    do_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request,
                    "Welcome to That Vacation Travel, we have sent you an email with the details of your approval.")
                    return redirect("/")
        else:
            messages.info(request,"Registro inválido revise los campos del formulario")

    return render(request, "register.html", {'form': form})




def send_registration_email(*emails):
    subject = 'That Vacation Registrations'
    message = ('Your approval is pending you sending us the information we requested '
               'through a document that we sent to your email. Once your approval is '
               'received, it will be ready in 72 hours. Thank you very much for '
               'registering for "That Vacation"')
    from_email = 'thatvacationtravel@gmail.com'
    recipient_list = list(emails)

    email = EmailMessage(subject, message, from_email, recipient_list)

    pdf_file_path = '/home/tvacation/thatvacation/static/b2bform/B2B Registration_Form.pdf'

    if os.path.exists(pdf_file_path):
        email.attach_file(pdf_file_path)

    email.send(fail_silently=False)



def error(request):
    return render(request, 'error403.html', status=403)



def logout(request):
    auth.logout(request)
    return redirect('/')


from django.db.models import Min, F, Subquery, OuterRef
from itertools import groupby
import logging


logger = logging.getLogger(__name__)

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def get_price_variable(adultos, ninos, child1_age, child2_age):
    if adultos == 1 and ninos == 0:
        return 'oneAdult'
    elif adultos == 2 and ninos == 0:
        return 'twoAdult'
    elif adultos == 3 and ninos == 0:
        return 'threeAdult'
    elif adultos == 4 and ninos == 0:
        return 'fourAdult'
    elif adultos == 1 and ninos == 1:
        if child1_age <= 11:
            return 'oneAdult1JrCh'
        else:
            return 'oneAdult1Ch'
    elif adultos == 1 and ninos == 2:
        if child1_age <= 11 and child2_age <= 11:
            return 'oneAdult2JrCh'
        elif child1_age >= 12 and child2_age >= 12:
            return 'oneAdult2Ch'
        elif child1_age >=12 and child2_age <=11:
            return 'oneAdult1Ch1JrCh'
        else:
            return 'oneAdult2JrCh'

    elif adultos == 2 and ninos == 1:
        if child1_age >= 12:
            return 'twoAdult1Ch'
        else:
            return 'twoAdult1JrCh'
    elif adultos == 2 and ninos == 2:
        if child1_age <= 11 and child2_age <= 11:
            return 'twoAdult2JrCh'
        elif child1_age >= 12 and child2_age <= 11:
            return 'twoAdult1Ch1JrCh'
        elif child1_age <=11 and child2_age >=12:
            return 'twoAdult1Ch1JrCh'
        else:
            return 'twoAdult2Ch'
    else:
        return None




def categorizar_cabinas1(cruises):
    grouped_cruceros = {
        'Inside': [],
        'Ocean View': [],
        'Balcony': [],
        'Suite': [],
        'Yacht Club': []
    }

    for crucero in cruises:
        category = crucero['category']

        if category.startswith('I'):
            grouped_cruceros['Inside'].append(crucero)
        elif category.startswith('O'):
            grouped_cruceros['Ocean View'].append(crucero)
        elif category.startswith('B'):
            grouped_cruceros['Balcony'].append(crucero)
        elif category.startswith('S'):
            grouped_cruceros['Suite'].append(crucero)
        elif category.startswith('Y'):
            grouped_cruceros['Yacht Club'].append(crucero)

    return grouped_cruceros



import math

def calculate_total_person_price(cruise, price_variable, total_participants):
    all_attributes = {}
    for attr in dir(cruise):
        try:
            value = getattr(cruise, attr)
            if not callable(value) and not isinstance(value, models.Manager) and not attr.startswith("__"):
                all_attributes[attr] = value
        except AttributeError:
            continue

    price = getattr(cruise, price_variable, None)
    if price is None:
        return None, None, None

    gftA = all_attributes.get('gftA', Decimal('0'))
    tax_total = total_participants * gftA
    total = tax_total + price
    total_person = total / total_participants

    return total_person, price, all_attributes




from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
@usuario_aprobado_required
def search_bookings(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('query', '').strip()
        page_number = request.GET.get('page', 1)
        user = request.user

        if query:
            if user.is_superuser:
                bookings_by_number = Booking.objects.filter(
                    booking_number__icontains=query
                )
                bookings_by_name = Booking.objects.filter(
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query)
                )
                bookings_by_uniqueid = Booking.objects.filter(
                    unique_id__icontains=query
                )
                bookings = bookings_by_number | bookings_by_name | bookings_by_uniqueid
            else:
                bookings_by_number = Booking.objects.filter(
                    booking_number__icontains=query,
                    user=user
                )
                bookings_by_name = Booking.objects.filter(
                    (Q(first_name__icontains=query) | Q(last_name__icontains=query)),
                    user=user
                )
                bookings_by_uniqueid = Booking.objects.filter(
                    booking_unique_id__icontains=query,
                    user=user
                )
                bookings = bookings_by_number | bookings_by_name | bookings_by_uniqueid
        else:
            bookings = Booking.objects.none()

        bookings = bookings.order_by('-created_at')
        paginator = Paginator(bookings, 10)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        results = list(page_obj.object_list.values('booking_number', 'ship', 'departure_day', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'balance'))
        return JsonResponse({
            'results': results,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


from collections import defaultdict
import pandas as pd




@login_required
@usuario_aprobado_required
def myaccounts(request):
    form = CruiseSearchForm1()
    profile_form = UserProfileForm(instance=request.user)
    hotel_search_form = HotelSearchForm()
    ages = list(range(0, 18))
    all_attributes = {}
    user_invoices = []

    if request.user.is_staff:
        my_earnings = InvoiceCustomer.objects.all().order_by('-current_datetime')
        earnings_with_invoices = []

        for earning in my_earnings:
            cruise = Cruise.objects.filter(cruiseID=earning.cruise).first()
            pay_date = cruise.sailingDate if cruise else None
            earnings_with_invoices.append({
                'username': earning.user.username,
                'booking_no': earning.booking_no,
                'comission_agent': earning.comission_agent,
                'invoice_date': earning.current_datetime,
                'pay_date': pay_date,
            })
    else:
        user_invoices = Booking.objects.filter(user=request.user)
        my_earnings = InvoiceCustomer.objects.filter(user=request.user).order_by('-current_datetime')

        invoice_dates = {invoice.booking_number: invoice.created_at for invoice in user_invoices}

        earnings_with_invoices = []
        for earning in my_earnings:
            cruise = Cruise.objects.filter(cruiseID=earning.cruise).first()
            pay_date = cruise.sailingDate if cruise else None
            earnings_with_invoices.append({
                'booking_no': earning.booking_no,
                'comission_agent': earning.comission_agent,
                'invoice_date': invoice_dates.get(earning.booking_no, None),
                'pay_date': pay_date,
            })

    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                form = CruiseSearchForm1(request.POST)
                if form.is_valid():
                    adultos = safe_int(form.cleaned_data.get('adultos'))
                    ninos = safe_int(form.cleaned_data.get('ninos', 0))
                    child1_age = safe_int(request.POST.get('child1_age', 0))
                    child2_age = safe_int(request.POST.get('child2_age', 0))
                    price_variable = get_price_variable(adultos, ninos, child1_age, child2_age)
                    total_participants = safe_int(adultos) + safe_int(ninos)

                    if not price_variable:
                        return JsonResponse({'errors': 'Combinación de adultos y niños no válida.'}, status=400)

                    destination = form.cleaned_data.get('destination')
                    port_choices = form.get_port_choices(destination)
                    form.fields['port'].choices = port_choices

                    start_date = form.cleaned_data.get('departure_date')
                    end_date = form.cleaned_data.get('departure_end_date')
                    port_code = form.cleaned_data.get('port')

                    cruises = Cruise.objects.filter(
                        sailingDate__range=(start_date, end_date),
                        nowAvailable=True
                    )

                    if destination:
                        related_ports = Port.objects.filter(destination=destination)

                        if port_code and port_code != "Any Port":
                            cruises = cruises.filter(sailingPort=port_code)
                        else:
                            cruises = cruises.filter(sailingPort__in=related_ports.values_list('port_code', flat=True))

                    cruises = cruises.exclude(
                        fareDesc=''
                    ).annotate(
                        min_price=Min(price_variable)
                    ).filter(
                        min_price__gt=0
                    ).order_by('cruiseID', 'min_price')

                    cruises_price_max = cruises.filter(
                        fareDesc='BROCHURE RATES'
                    ).annotate(
                        max_price=Min(price_variable)
                    ).filter(
                        max_price__gt=0
                    ).order_by('cruiseID', 'max_price')

                    for attr in dir(cruises):
                        try:
                            value = getattr(cruises, attr)
                            if not callable(value) and not isinstance(value, models.Manager) and not attr.startswith("__"):
                                all_attributes[attr] = value
                        except AttributeError:
                            continue
                    cruise_data = []

                    for cruise_id, group in groupby(cruises, lambda x: x.cruiseID):
                        min_price_cruise = min(group, key=lambda x: x.min_price or float('inf'))
                        max_price_cruise = next(
                            (c for c in cruises_price_max if c.cruiseID == min_price_cruise.cruiseID),
                            None
                        )
                        
                        fare_code_max = None

                        if min_price_cruise is not None:
                            total_person, price, all_attributes = calculate_total_person_price(min_price_cruise, price_variable, total_participants)
                            fare_desc_min = min_price_cruise.fareDesc
                            
                            if fare_desc_min == "ESCAPE TO SEA CRUISE ONLY":
                                price_max = None  
                            else:
                                price_max = max_price_cruise.max_price / total_participants if max_price_cruise else None
                                fare_code_max = max_price_cruise.fareCode if max_price_cruise else None
                                fecha_salida = max_price_cruise.sailingDate if max_price_cruise else None
                                print(f"Fare Code del barco con precio máximo: {fare_code_max}, fecha salida: {fecha_salida}")

                                if fare_desc_min == "FLASH SALE CRUISE ONLY":
                                    print(f"Precio máximo para FLASH SALE: {price_max}")
                                elif fare_desc_min == "WINTER SALES":
                                    price_max = None

                            if price is not None:
                                port_name = Port.objects.get(port_code=min_price_cruise.sailingPort).port_name

                                cruise_data.append({
                                    'cruiseID': min_price_cruise.cruiseID,
                                    'sailingDate': min_price_cruise.sailingDate.strftime('%Y-%m-%d'),
                                    'returnDate': (min_price_cruise.sailingDate + timedelta(days=min_price_cruise.nights)).strftime('%Y-%m-%d'),
                                    'shipName': min_price_cruise.shipName,
                                    'itinDesc': min_price_cruise.itinDesc,
                                    'nights': min_price_cruise.nights,
                                    'sailingPort': min_price_cruise.sailingPort,
                                    'portName': port_name,
                                    'oneAdult': safe_int(getattr(min_price_cruise, 'oneAdult', 0)),
                                    'twoAdult': safe_int(getattr(min_price_cruise, 'twoAdult', 0)),
                                    'threeAdult': safe_int(getattr(min_price_cruise, 'threeAdult', 0)),
                                    'fourAdult': safe_int(getattr(min_price_cruise, 'fourAdult', 0)),
                                    'oneAdult1Ch': safe_int(getattr(min_price_cruise, 'oneAdult1Ch', 0)),
                                    'oneAdult2Ch': safe_int(getattr(min_price_cruise, 'oneAdult2Ch', 0)),
                                    'oneAdult3Ch': safe_int(getattr(min_price_cruise, 'oneAdult3Ch', 0)),
                                    'twoAdult1Ch': safe_int(getattr(min_price_cruise, 'twoAdult1Ch', 0)),
                                    'twoAdult1JrCh': safe_int(getattr(min_price_cruise, 'twoAdult1JrCh', 0)),
                                    'twoAdult2Ch': safe_int(getattr(min_price_cruise, 'twoAdult2Ch', 0)),
                                    'twoAdult1Ch1JrCh': safe_int(getattr(min_price_cruise, 'twoAdult1Ch1JrCh', 0)),
                                    'twoAdult2JrCh': safe_int(getattr(min_price_cruise, 'twoAdult2JrCh', 0)),
                                    'price': price,
                                    'gftA': safe_int(getattr(min_price_cruise, 'gftA', 0)),
                                    'fareStartDate': min_price_cruise.fareStartDate.strftime('%Y-%m-%d'),
                                    'fareEndDate': min_price_cruise.fareEndDate.strftime('%Y-%m-%d'),
                                    'priceType': min_price_cruise.priceType,
                                    'category': min_price_cruise.category,
                                    'fareCode': min_price_cruise.fareCode,
                                    'fareDesc': min_price_cruise.fareDesc,
                                    'total_price': price + (safe_int(getattr(min_price_cruise, 'gftA', 0)) * total_participants),
                                    'total_participants': total_participants,
                                    'tax': safe_int(getattr(min_price_cruise, 'gftA', 0)) * total_participants,
                                    'price_per_person': total_person,
                                    'price_maximo': price_max + (safe_int(getattr(min_price_cruise, 'gftA', 0)) * total_participants) if price_max is not None else 0,
                                    'ages': ages,
                                    'all_attributes': all_attributes,
                                    'price_variable': price_variable,
                                    'fare_code_max':fare_code_max,
                                })

                    categorized_cruises = categorizar_cabinas1(cruise_data)

                    html = render_to_string('partial_cruise_list.html', {
                        'categorized_cruises': categorized_cruises,
                        'all_attributes': all_attributes,
                        'price_variable': price_variable
                    }, request)

                    return JsonResponse({'html': html})
                else:
                    errors = dict(form.errors.items())
                    return JsonResponse({'errors': errors}, status=400)
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                return JsonResponse({'errors': 'Error interno del servidor: {}'.format(str(e))}, status=500)

        elif 'action' in request.POST:
            try:
                if request.POST['action'] == 'update_profile':
                    profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
                    if profile_form.is_valid():
                        profile_form.save()
                        messages.success(request, 'Perfil actualizado correctamente.')
                        return redirect('myaccounts')
                    else:
                        messages.error(request, 'Error al actualizar el perfil.')
                elif request.POST['action'] == 'search_hotel':
                    hotel_search_form = HotelSearchForm(request.POST)
                    if hotel_search_form.is_valid():
                        hotel_data = []
                        messages.success(request, 'Búsqueda de hoteles realizada con éxito.')
                        context = {'hotel_data': hotel_data, 'hotel_search_form': hotel_search_form}
                        return render(request, 'myaccounts.html', context)
                    else:
                        messages.error(request, 'Error en el formulario de búsqueda de hoteles.')
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                messages.error(request, 'Error interno del servidor.')

    stats_by_day = defaultdict(float)

    for invoice in user_invoices:
        fecha = invoice.created_at
        stats_by_day[fecha.day] += float(invoice.total_to_pay)

    days = list(range(1, 32))
    totals_by_day = [stats_by_day[day] for day in days]

    total_por_mes = [
        sum(float(invoice.total_to_pay) for invoice in user_invoices if invoice.created_at.month == month)
        for month in range(1, 13)
    ]

    montos_reservas = [
        [float(invoice.balance) for invoice in user_invoices if invoice.created_at.month == month]
        for month in range(1, 13)
    ]

    meses = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
    ]

    df_totals = pd.DataFrame({
        'Days': days,
        'Total per Day': totals_by_day,
    })

    fig = px.line(df_totals, x='Days', y='Total per Day', title='Earnings Statistics')
    config = {
        'displayModeBar': True,
        'modeBarButtonsToRemove': [
            'toImage',
            'resetScale2d',
            'autoScale2d',
            'hoverCompareCartesian',
            'hoverClosestCartesian',

            'zoomIn2d',
            'zoomOut2d',
            'select2d',
            'lasso2d',
        ],
        'modeBarButtonsToAdd': [
            'zoom2d',
            'pan2d'
        ],
        'showSendToCloud': False,
        'showEditInChartStudio': False,
    }
    graph_html = fig.to_html(full_html=False, config=config)

    def safe_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0

    total_earnings = sum([safe_float(earning.comission_agent) for earning in my_earnings])
    total_earnings = round(total_earnings, 2)

    context = {
        'form': form,
        'profile_form': profile_form,
        'hotel_search_form': hotel_search_form,
        'ages': ages,
        'all_attributes': all_attributes,
        'totals': json.dumps(total_por_mes),
        'reservas': json.dumps(montos_reservas),
        'months': json.dumps(meses),
        'totals_by_day': json.dumps(totals_by_day),
        'days': json.dumps(days),
        'graph_html': graph_html,
        'my_earnings':earnings_with_invoices,
        'total_earnings':total_earnings,

    }

    return render(request, 'myaccounts.html', context)




def load_ports(request):
    destino_id = request.GET.get('destino_id')
    ports = Port.objects.filter(destination__id=destino_id)
    ports_data = [{'port_code': port.port_code, 'port_name': port.port_name} for port in ports]
    return JsonResponse(ports_data, safe=False)



def calcular_precio(request):
    crucero_id = request.GET.get('crucero_id')
    num_adultos = int(request.GET.get('num_adultos', 1))
    num_ninos = int(request.GET.get('num_ninos', 0))
    fare_desc = request.GET.get('fare_desc')

    crucero = Cruise.objects.filter(cruiseID=crucero_id, fareDesc=fare_desc).first()
    if not crucero:
        return JsonResponse({'error': 'Crucero no encontrado'}, status=404)

    precio = None
    if num_adultos == 1 and num_ninos == 0:
        precio = crucero.oneAdult
    elif num_adultos == 2 and num_ninos == 0:
        precio = crucero.twoAdult
    elif num_adultos == 3 and num_ninos == 0:
        precio = crucero.threeAdult
    elif num_adultos == 4 and num_ninos == 0:
        precio = crucero.fourAdult
    elif num_adultos == 2 and num_ninos == 1:
        precio = crucero.twoAdult1Ch
    elif num_adultos == 2 and num_ninos == 2:
        precio = crucero.twoAdult2Ch
    elif num_adultos == 1 and num_ninos == 1:
        precio = crucero.oneAdult1Ch
    elif num_adultos == 1 and num_ninos == 1:
        precio = crucero.oneAdult1JrCh
    elif num_adultos == 2 and num_ninos == 1:
        precio = crucero.twoAdult1JrCh
    elif num_adultos == 2 and num_ninos == 1 and num_ninos == 1:
        precio = crucero.twoAdult1Ch1JrCh
    elif num_adultos == 2 and num_ninos == 2:
        precio = crucero.twoAdult2JrCh

    return JsonResponse({'precio': precio})


from django.db import models
from django.utils.html import escapejs
from django.template.loader import render_to_string
from django.core.serializers.json import DjangoJSONEncoder
import random


def obtener_numero_pasajeros(price_variable):
    mapeo_pasajeros = {
        'oneAdult': 1,
        'twoAdult': 2,
        'threeAdult': 3,
        'fourAdult': 4,
        'twoAdult1Ch': 3,
        'twoAdult2Ch': 4,
        'oneAdult1Ch': 2,
        'oneAdult1JrCh': 2,
        'twoAdult1JrCh': 3,
        'twoAdult1Ch1JrCh': 4,
        'twoAdult2JrCh': 4
    }
    return mapeo_pasajeros.get(price_variable, 1)


def obtener_codigos_items(texto_items, categoria):
    codigos = re.findall(r'OBS:([A-Z0-9]+):M', texto_items)
    return codigos

def get_items_por_categoria(fare_code, categoria, codigos_items):
    items = Item.objects.filter(fare_cd=fare_code, category=categoria, code__in=codigos_items)
    return items

def extraer_categoria(categoria_completa):
    match = re.match(r'^[A-Z0-9]+', categoria_completa)
    if match:
        return match.group(0)
    return None


import concurrent.futures
from django.core.cache import cache


def obtener_codigo_alternativo(categoria_code, ship_name):
    existe_categoria = cabinDetail.objects.filter(
        ship_name=ship_name,
        category_code=categoria_code
    ).exists()

    if not existe_categoria:
        if categoria_code == "IB":
            codigo_alternativo = "323"
            existe_alternativa = cabinDetail.objects.filter(
                ship_name=ship_name,
                category_code=codigo_alternativo
            ).exists()
            if existe_alternativa:
                return codigo_alternativo

    return categoria_code


def experience(request, crucero_id, priceVariable):
    logger = logging.getLogger('django')

    crucero = Cruise.objects.filter(cruiseID=crucero_id, nowAvailable="True").exclude(**{priceVariable: None})

    if not crucero:
        return render(request, 'error.html', {'message': 'Crucero no encontrado.'})

    total_pasajeros = obtener_numero_pasajeros(priceVariable)

    selected_fare_desc = None
    if request.GET.get('cruise_only'):
        selected_fare_desc = "ESCAPE TO SEA CRUISE ONLY"
    elif request.GET.get('wifi_included'):
        selected_fare_desc = "DRINKS WIFI OBC INCLUDED"
    elif request.GET.get('winter_sale'):
        selected_fare_desc = "WINTER SALE"
    elif request.GET.get('drinks_and_obc_included'):
        selected_fare_desc = "DRINKS AND OBC INCLUDED"
    elif request.GET.get("cruise_with_drinks"):
        selected_fare_desc = "CRUISE WITH DRINKS INCLUDED"
    elif request.GET.get("flash_sale_drinks"):
        selected_fare_desc = "FLASH SALE DRINKS"
    elif request.GET.get("flash_sale_cruise_only"):
        selected_fare_desc = "FLASH SALE CRUISE ONLY"

    if not selected_fare_desc:
        if crucero.exists():
            cruise_only_option = crucero.filter(fareDesc__in=["ESCAPE TO SEA CRUISE ONLY", "FLASH SALE CRUISE ONLY"]).first()

            if cruise_only_option:
                selected_fare_desc = cruise_only_option.fareDesc
            else:
                selected_fare_desc = crucero.first().fareDesc  
        else:
            selected_fare_desc = None

    cruceros_misma_categoria = crucero.filter(fareDesc=selected_fare_desc) if selected_fare_desc else crucero

    if not cruceros_misma_categoria:
        return render(request, 'error.html', {'message': 'No hay cruceros disponibles para la tarifa seleccionada.'})

    fare_descs = list(set(crucero.fareDesc for crucero in crucero))

    all_attributes = {}
    crucero1 = cruceros_misma_categoria.first()
    for attr in dir(crucero1):
        try:
            value = getattr(crucero1, attr)
            if not callable(value) and not isinstance(value, models.Manager) and not attr.startswith("__"):
                all_attributes[attr] = value
        except AttributeError:
            continue

    price = getattr(crucero1, priceVariable, None)
    if price is None:
        return render(request, 'error.html', {'message': 'Precio no disponible para esta configuración de pasajeros.'})

    fare_descriptions = [
        "ESCAPE TO SEA CRUISE ONLY",
        "DRINKS WIFI OBC INCLUDED",
        "WINTER SALE",
        "CRUISE WITH DRINKS INCLUDED",
        "FLASH SALE DRINKS",
        "FLASH SALE CRUISE ONLY",
        "DRINKS AND OBC INCLUDED",
    ]

    fare_prices = {}

    cruise_only_fare = crucero.filter(fareDesc="ESCAPE TO SEA CRUISE ONLY").first()
    flash_cruise_only_fare = crucero.filter(fareDesc="FLASH SALE CRUISE ONLY").first()

    price_cruise_only = Decimal('0')
    price_flash_cruise_only = Decimal('0')

    if cruise_only_fare:
        price_cruise_only = getattr(cruise_only_fare, priceVariable, Decimal('0'))

    if flash_cruise_only_fare:
        price_flash_cruise_only = getattr(flash_cruise_only_fare, priceVariable, Decimal('0'))

    for fare_desc in fare_descriptions:
        fare_key = fare_desc.replace(" ", "_")
        crucero_fare = crucero.filter(fareDesc=fare_desc).first()

        if crucero_fare:
            price_fare = getattr(crucero_fare, priceVariable, Decimal('0'))
        else:
            price_fare = Decimal('0')

        fare_prices[fare_key] = (price_fare - price_cruise_only - price_flash_cruise_only) / total_pasajeros if total_pasajeros > 0 else Decimal('0')

    gftA = all_attributes.get('gftA', Decimal('0'))
    tax_total = total_pasajeros * gftA
    total = tax_total + price
    total_person = total / total_pasajeros

    ship_names = [crucero.shipName for crucero in cruceros_misma_categoria]
    categoria_codes = [extraer_categoria(crucero.category) for crucero in cruceros_misma_categoria]

    if check_cruise():
        cruise_msc()
        return HttpResponse("")

    itinerario = Itinerary.objects.filter(cruise_id=crucero1.cruiseID, itinerary_cd=crucero1.itinCd)

    previous_port = None
    for itinerary in itinerario:
        itinerary.new_day = (previous_port != itinerary.arrival_port)
        previous_port = itinerary.arrival_port

    context = {}

    categoria_codes_mapeados = []
    for code in categoria_codes:
        codigo_mapeado = obtener_codigo_alternativo(code, ship_names[0])
        categoria_codes_mapeados.append(codigo_mapeado)


    experiencia = cabinDetail.objects.filter(
        ship_name__in=ship_names,
        category_code__in=categoria_codes_mapeados,

    ).filter(
        Q(category_code__in=categoria_codes_mapeados) | Q(cabin_number__startswith='G00000')
    )


    all_cabinas = []

    def fetch_cabins_for_category(category):
        cache_key = f"cabins_{crucero1.cruiseID}_{category}"
        cached_cabins = cache.get(cache_key)

        if cached_cabins:
            print(f"Usando caché para la categoría {category}")
            return cached_cabins

        password_hash = calcula_hash_sha256("Mscx1x2x3!")
        cabin_headers = {
            'Content-Type': 'text/xml',
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': password_hash,
            'AgentID': 'US159929',
        }

        cabin_xml_data = f'''
            <DtsCruiseCabinAvailabilityRequest xmlns="DTS">
                <BookingContext>
                    <AdvertisingSource />
                    <BookingContactName>1</BookingContactName>
                    <LoyalityCardMemberLevel />
                    <NoAdults>{total_pasajeros}</NoAdults>
                    <BookingChannel>XML</BookingChannel>
                </BookingContext>
                <CruiseComponent>
                    <CruiseID>{crucero1.cruiseID}</CruiseID>
                    <CategoryCode>{category}</CategoryCode>
                    <PromotionCode></PromotionCode>
                </CruiseComponent>
            </DtsCruiseCabinAvailabilityRequest>
        '''

        try:
            response = requests.post(
                'https://wsrv3.msccruises.com/mscbee/services/cabin/getcabins/',
                headers=cabin_headers,
                data=cabin_xml_data.encode('utf-8')
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {'DTS': 'DTS'}

            available_cabins = root.findall('.//DTS:AvailableCabin', namespaces=ns)

            cabinas = []
            for cabin in available_cabins:
                cabin_number = cabin.find('DTS:CabinNo', namespaces=ns).text
                cabinas.append({
                    "cabin_number": cabin_number,
                    "category_code": category,
                })

            cache.set(cache_key, cabinas, timeout=600)

            print(f"Cabinas disponibles obtenidas para la categoría {category}:")
            for cabin in cabinas:
                print(f"Category: {cabin['category_code']} - Cabin Number: {cabin['cabin_number']}")

            return cabinas

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener cabinas disponibles para la categoría {category}: {str(e)}")
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_cabins_for_category, categoria_codes)
    for result in results:
        all_cabinas.extend(result)

    context['available_cabins'] = all_cabinas

    cabinas_disponibles_api = {cabin['cabin_number'] for cabin in all_cabinas}

    experiencia_por_categoria = {}

    for cabina in all_cabinas:
        if cabina["cabin_number"] == "G00000":
            if cabina["category_code"] not in experiencia_por_categoria:
                experiencia_por_categoria[cabina["category_code"]] = []
            experiencia_por_categoria[cabina["category_code"]].append({
                "ship_name": cabina.get("ship_name", "Unknown"),
                "category_code": cabina["category_code"],
                "category_desc": cabina.get("category_desc", "Unknown"),
                "cabin_number": cabina["cabin_number"],
            })

    for exp in experiencia:
        if exp.cabin_number in cabinas_disponibles_api:
            if exp.category_code not in experiencia_por_categoria:
                experiencia_por_categoria[exp.category_code] = []
            experiencia_por_categoria[exp.category_code].append({
                "ship_name": exp.ship_name,
                "category_code": exp.category_code,
                "category_desc": exp.category_desc,
                "cabin_number": exp.cabin_number,
            })

    experiencia_por_categoria_random = {}
    for category, details in experiencia_por_categoria.items():
        experiencia_por_categoria_random[category] = random.choice(details) if details else None

    context['experiencia_por_categoria'] = experiencia_por_categoria
    context['experiencia_por_categoria_random'] = experiencia_por_categoria_random

    experiencia_por_categoria_json = {category: json.dumps(details, cls=DjangoJSONEncoder) for category, details in experiencia_por_categoria.items()}

    items_por_categoria = {}
    crucero_data = []
    codigos_items = []
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)
        logger.debug(f"Crucero ID: {crucero.id}, Fare Code: {crucero.fareCode}, Categoría: {categoria}, Códigos de Ítems: {codigos_items}")

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_categoria[categoria] = items_list
        crucero_data.append({
            'id': crucero.id,
            'fare_code': crucero.fareCode,
            'categoria': categoria,
            'codigos_items': codigos_items,
            'items': items_list
        })

    items_por_crucero_categoria = {}
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_crucero_categoria[crucero.id] = {
            'categoria': categoria,
            'items': items_list,
            'codigos_items': codigos_items,
            'fare_code': crucero.fareCode,
            'id': crucero.id
        }
        crucero.categoria_extraida = categoria

    grouped_cruceros = {}

    for crucero in cruceros_misma_categoria:
        categoria_mapeada = obtener_codigo_alternativo(crucero.categoria_extraida, crucero.shipName)

        first_letter = categoria_mapeada[0].upper()

        if first_letter not in grouped_cruceros:
            grouped_cruceros[first_letter] = []

        grouped_cruceros[first_letter].append(crucero)

    precios_inside = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('I') and getattr(crucero, priceVariable) is not None]
    precio_min_inside = min(precios_inside) if precios_inside else None

    precios_oceanview = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('O') and getattr(crucero, priceVariable) is not None]
    precio_min_oceanview = min(precios_oceanview) if precios_oceanview else None

    precios_balcon = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('B') and getattr(crucero, priceVariable) is not None]
    precio_min_balcon = min(precios_balcon) if precios_balcon else None

    precios_suite = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('S') and getattr(crucero, priceVariable) is not None]
    precio_min_suite = min(precios_suite) if precios_suite else None

    precios_yachtclub = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('Y') and getattr(crucero, priceVariable) is not None]
    precio_min_yachtclub = min(precios_yachtclub) if precios_yachtclub else None

    def format_time_24_to_12(time_str):
        try:
            if not time_str:
                return ""
            time_obj = datetime.strptime(time_str, "%H%M")
            return time_obj.strftime("%I:%M %p").lstrip('0').replace(' 0', ' ')
        except ValueError:
            return time_str

    itinerario_reorganizado = []
    for idx, item in enumerate(itinerario):
        if item.departure_port_name == "At Sea":
            time_str = ""
        else:
            prev_item = itinerario[idx - 1] if idx > 0 else None
            current_item = item

            prev_arrival_time = format_time_24_to_12(prev_item.arrival_time) if prev_item else ""
            current_departure_time = format_time_24_to_12(current_item.departure_time)

            if prev_arrival_time and current_departure_time:
                time_str = f"{prev_arrival_time} — {current_departure_time}"
            elif prev_arrival_time:
                time_str = f"{prev_arrival_time}"
            elif current_departure_time:
                time_str = f"{current_departure_time}"
            else:
                time_str = ""

        itinerario_reorganizado.append({
            'dia': idx + 1,
            'port_name': item.departure_port_name,
            'time': time_str
        })

    if itinerario.exists():
        ultimo_item = itinerario.last()
        if ultimo_item.arrival_port_name == "At Sea":
            time_str = ""
        else:
            time_str = format_time_24_to_12(ultimo_item.arrival_time)

        itinerario_reorganizado.append({
            'dia': len(itinerario) + 1,
            'port_name': ultimo_item.arrival_port_name,
            'time': time_str
        })

    cabins_by_category = {}
    for cabin in all_cabinas:
        category = cabin['category_code']
        if category not in cabins_by_category:
            cabins_by_category[category] = []
        cabins_by_category[category].append(cabin['cabin_number'])

    cabins_by_category_json = {category: json.dumps(cabins, cls=DjangoJSONEncoder) for category, cabins in cabins_by_category.items()}


    context = {
        'fare_prices': fare_prices,
        'available_cabins': cabins_by_category,
        'experiencia_por_categoria_json': cabins_by_category_json,
        'itinerario_reorganizado': itinerario_reorganizado,
        'crucero': crucero,
        'precio_min_inside': precio_min_inside,
        'precio_min_oceanview': precio_min_oceanview,
        'precio_min_balcon': precio_min_balcon,
        'precio_min_suite': precio_min_suite,
        'precio_min_yachtclub': precio_min_yachtclub,
        'experiencia_por_categoria_json': experiencia_por_categoria_json,
        'cruceros_misma_categoria': cruceros_misma_categoria,
        'grouped_cruceros': grouped_cruceros,
        'experiencia': experiencia,
        'experiencia_por_categoria': experiencia_por_categoria_random,
        'itinerario': itinerario,
        'price_variable': priceVariable,
        'price': price,
        'all_attributes': all_attributes,
        'items_por_crucero_categoria': items_por_crucero_categoria,
        'items_por_categoria': items_por_categoria,
        'codigos_items': codigos_items,
        'categoria_codes': categoria_codes,
        'crucero_data': crucero_data,
        'total_pasajeros': total_pasajeros,
        'total_person': round(price / total_pasajeros, 2) if total_pasajeros else 0,
        'fare_descs': fare_descs,
        'fare_desc': crucero1.fareDesc if crucero1 else None,
        'crucero1': crucero1,
    }

    logger.debug(f"Contexto: {context}")


    return render(request, 'experience.html', context)


from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
import logging
import concurrent.futures
import requests
import xml.etree.ElementTree as ET
import random
from .models import Cruise, Itinerary, cabinDetail, Item
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
import logging
import concurrent.futures
import requests
import xml.etree.ElementTree as ET
import random
from .models import Cruise, Itinerary, cabinDetail, Item
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from decimal import Decimal
import logging
import concurrent.futures
import requests
import xml.etree.ElementTree as ET
import random
from .models import Cruise, Itinerary, cabinDetail, Item
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from django.http import JsonResponse
from decimal import Decimal
import logging
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from decimal import Decimal
import logging

def endpoint_experience(request, crucero_id, priceVariable):
    logger = logging.getLogger('django')
    crucero = Cruise.objects.filter(cruiseID=crucero_id, nowAvailable="True").exclude(**{priceVariable: None})

    if not crucero:
        return render(request, 'error.html', {'message': 'Crucero no encontrado.'})

    total_pasajeros = obtener_numero_pasajeros(priceVariable)

    selected_fare_desc = None
    if request.GET.get('cruise_only'):
        selected_fare_desc = "ESCAPE TO SEA CRUISE ONLY"
    elif request.GET.get('wifi_included'):
        selected_fare_desc = "DRINKS WIFI OBC INCLUDED"
    elif request.GET.get('winter_sale'):
        selected_fare_desc = "WINTER SALE"
    elif request.GET.get("cruise_with_drinks"):
        selected_fare_desc = "CRUISE WITH DRINKS INCLUDED"
    elif request.GET.get("flash_sale_drinks"):
        selected_fare_desc = "FLASH SALE DRINKS"
    elif request.GET.get("flash_sale_cruise_only"):
        selected_fare_desc = "FLASH SALE CRUISE ONLY"

    if not selected_fare_desc:
        if crucero.exists():
            cruise_only_option = crucero.filter(fareDesc="ESCAPE TO SEA CRUISE ONLY").first()
            if cruise_only_option:
                selected_fare_desc = "ESCAPE TO SEA CRUISE ONLY"
            else:
                for c in crucero:
                    if c.fareDesc != 'WINTER SALE':
                        selected_fare_desc = c.fareDesc
                        break
        else:
            selected_fare_desc = None

    cruceros_misma_categoria = crucero.filter(fareDesc=selected_fare_desc) if selected_fare_desc else crucero

    if not cruceros_misma_categoria:
        return render(request, 'error.html', {'message': 'No hay cruceros disponibles para la tarifa seleccionada.'})

    fare_descs = list(set(crucero.fareDesc for crucero in crucero))

    all_attributes = {}
    crucero1 = cruceros_misma_categoria.first()
    for attr in dir(crucero1):
        try:
            value = getattr(crucero1, attr)
            if not callable(value) and not isinstance(value, models.Manager) and not attr.startswith("__"):
                all_attributes[attr] = value
        except AttributeError:
            continue

    price = getattr(crucero1, priceVariable, None)
    if price is None:
        return render(request, 'error.html', {'message': 'Precio no disponible para esta configuración de pasajeros.'})

    fare_descriptions = [
        "ESCAPE TO SEA CRUISE ONLY",
        "DRINKS WIFI OBC INCLUDED",
        "WINTER SALE",
        "CRUISE WITH DRINKS INCLUDED",
        "FLASH SALE DRINKS",
        "FLASH SALE CRUISE ONLY"
    ]

    fare_prices = {}

    cruise_only_fare = crucero.filter(fareDesc="ESCAPE TO SEA CRUISE ONLY").first()
    flash_cruise_only_fare = crucero.filter(fareDesc="FLASH SALE CRUISE ONLY").first()

    price_cruise_only = Decimal('0')
    price_flash_cruise_only = Decimal('0')

    if cruise_only_fare:
        price_cruise_only = getattr(cruise_only_fare, priceVariable, Decimal('0'))

    if flash_cruise_only_fare:
        price_flash_cruise_only = getattr(flash_cruise_only_fare, priceVariable, Decimal('0'))

    for fare_desc in fare_descriptions:
        fare_key = fare_desc.replace(" ", "_")
        crucero_fare = crucero.filter(fareDesc=fare_desc).first()

        if crucero_fare:
            price_fare = getattr(crucero_fare, priceVariable, Decimal('0'))
        else:
            price_fare = Decimal('0')

        fare_prices[fare_key] = (price_fare - price_cruise_only - price_flash_cruise_only) / total_pasajeros if total_pasajeros > 0 else Decimal('0')


    gftA = all_attributes.get('gftA', Decimal('0'))
    tax_total = total_pasajeros * gftA
    total = tax_total + price
    total_person = total / total_pasajeros


    ship_names = [crucero.shipName for crucero in cruceros_misma_categoria]
    categoria_codes = [extraer_categoria(crucero.category) for crucero in cruceros_misma_categoria]

    if check_cruise():
        cruise_msc()
        return HttpResponse("")

    itinerario = Itinerary.objects.filter(cruise_id=crucero1.cruiseID, itinerary_cd=crucero1.itinCd)

    previous_port = None
    for itinerary in itinerario:
        itinerary.new_day = (previous_port != itinerary.arrival_port)
        previous_port = itinerary.arrival_port

    context = {}

    categoria_codes_mapeados = []
    for code in categoria_codes:
        codigo_mapeado = obtener_codigo_alternativo(code, ship_names[0])
        categoria_codes_mapeados.append(codigo_mapeado)


    experiencia = cabinDetail.objects.filter(
        ship_name__in=ship_names,
        category_code__in=categoria_codes_mapeados,

    ).filter(
        Q(category_code__in=categoria_codes_mapeados) | Q(cabin_number__startswith='G00000')
    )
    all_cabinas = []

    def fetch_cabins_for_category(category):
        cache_key = f"cabins_{crucero1.cruiseID}_{category}"
        cached_cabins = cache.get(cache_key)

        if cached_cabins:
            print(f"Usando caché para la categoría {category}")
            return cached_cabins

        password_hash = calcula_hash_sha256("Mscx1x2x3!")
        cabin_headers = {
            'Content-Type': 'text/xml',
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': password_hash,
            'AgentID': 'US159929',
        }

        cabin_xml_data = f'''
            <DtsCruiseCabinAvailabilityRequest xmlns="DTS">
                <BookingContext>
                    <AdvertisingSource />
                    <BookingContactName>1</BookingContactName>
                    <LoyalityCardMemberLevel />
                    <NoAdults>{total_pasajeros}</NoAdults>
                    <BookingChannel>XML</BookingChannel>
                </BookingContext>
                <CruiseComponent>
                    <CruiseID>{crucero1.cruiseID}</CruiseID>
                    <CategoryCode>{category}</CategoryCode>
                    <PromotionCode></PromotionCode>
                </CruiseComponent>
            </DtsCruiseCabinAvailabilityRequest>
        '''

        try:
            response = requests.post(
                'https://wsrv3.msccruises.com/mscbee/services/cabin/getcabins/',
                headers=cabin_headers,
                data=cabin_xml_data.encode('utf-8')
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {'DTS': 'DTS'}

            available_cabins = root.findall('.//DTS:AvailableCabin', namespaces=ns)

            cabinas = []
            for cabin in available_cabins:
                cabin_number = cabin.find('DTS:CabinNo', namespaces=ns).text
                cabinas.append({
                    "cabin_number": cabin_number,
                    "category_code": category,
                })

            cache.set(cache_key, cabinas, timeout=600)

            print(f"Cabinas disponibles obtenidas para la categoría {category}:")
            for cabin in cabinas:
                print(f"Category: {cabin['category_code']} - Cabin Number: {cabin['cabin_number']}")

            return cabinas

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener cabinas disponibles para la categoría {category}: {str(e)}")
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_cabins_for_category, categoria_codes)
    for result in results:
        all_cabinas.extend(result)

    context['available_cabins'] = all_cabinas

    cabinas_disponibles_api = {cabin['cabin_number'] for cabin in all_cabinas}

    experiencia_por_categoria = {}

    for cabina in all_cabinas:
        if cabina["cabin_number"] == "G00000":
            if cabina["category_code"] not in experiencia_por_categoria:
                experiencia_por_categoria[cabina["category_code"]] = []
            experiencia_por_categoria[cabina["category_code"]].append({
                "ship_name": cabina.get("ship_name", "Unknown"),
                "category_code": cabina["category_code"],
                "category_desc": cabina.get("category_desc", "Unknown"),
                "cabin_number": cabina["cabin_number"],
            })

    for exp in experiencia:
        if exp.cabin_number in cabinas_disponibles_api:
            if exp.category_code not in experiencia_por_categoria:
                experiencia_por_categoria[exp.category_code] = []
            experiencia_por_categoria[exp.category_code].append({
                "ship_name": exp.ship_name,
                "category_code": exp.category_code,
                "category_desc": exp.category_desc,
                "cabin_number": exp.cabin_number,
            })

    experiencia_por_categoria_random = {}
    for category, details in experiencia_por_categoria.items():
        experiencia_por_categoria_random[category] = random.choice(details) if details else None

    context['experiencia_por_categoria'] = experiencia_por_categoria
    context['experiencia_por_categoria_random'] = experiencia_por_categoria_random

    experiencia_por_categoria_json = {category: json.dumps(details, cls=DjangoJSONEncoder) for category, details in experiencia_por_categoria.items()}

    items_por_categoria = {}
    crucero_data = []
    codigos_items = []
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)
        logger.debug(f"Crucero ID: {crucero.id}, Fare Code: {crucero.fareCode}, Categoría: {categoria}, Códigos de Ítems: {codigos_items}")

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_categoria[categoria] = items_list
        crucero_data.append({
            'id': crucero.id,
            'fare_code': crucero.fareCode,
            'categoria': categoria,
            'codigos_items': codigos_items,
            'items': items_list
        })

    items_por_crucero_categoria = {}
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_crucero_categoria[crucero.id] = {
            'categoria': categoria,
            'items': items_list,
            'codigos_items': codigos_items,
            'fare_code': crucero.fareCode,
            'id': crucero.id
        }
        crucero.categoria_extraida = categoria

    grouped_cruceros = {}

    for crucero in cruceros_misma_categoria:
        categoria_mapeada = obtener_codigo_alternativo(crucero.categoria_extraida, crucero.shipName)

        first_letter = categoria_mapeada[0].upper()

        if first_letter not in grouped_cruceros:
            grouped_cruceros[first_letter] = []

        grouped_cruceros[first_letter].append(crucero)

    precios_inside = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('I') and getattr(crucero, priceVariable) is not None]
    precio_min_inside1 = min(precios_inside) if precios_inside else None
    precio_min_inside = (precio_min_inside1 + tax_total) / total_pasajeros if precio_min_inside1 else None

    precios_oceanview = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('O') and getattr(crucero, priceVariable) is not None]
    precio_min_oceanview1 = min(precios_oceanview) if precios_oceanview else None
    precio_min_oceanview = (precio_min_oceanview1 + tax_total) / total_pasajeros if precio_min_oceanview1 else None

    precios_balcon = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('B') and getattr(crucero, priceVariable) is not None]
    precio_min_balcon1 = min(precios_balcon) if precios_balcon else None
    precio_min_balcon = (precio_min_balcon1 + tax_total) / total_pasajeros if precio_min_balcon1 else None

    precios_suite = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('S') and getattr(crucero, priceVariable) is not None]
    precio_min_suite1 = min(precios_suite) if precios_suite else None
    precio_min_suite = (precio_min_suite1 + tax_total) / total_pasajeros if precio_min_suite1 else None

    precios_yachtclub = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('Y') and getattr(crucero, priceVariable) is not None]
    precio_min_yachtclub1 = min(precios_yachtclub) if precios_yachtclub else None
    precio_min_yachtclub = (precio_min_yachtclub1 + tax_total) / total_pasajeros if precio_min_yachtclub1 else None



    cabins_by_category = {}
    for cabin in all_cabinas:
        category = cabin['category_code']
        if category not in cabins_by_category:
            cabins_by_category[category] = []
        cabins_by_category[category].append(cabin['cabin_number'])

    cabins_by_category_json = {category: json.dumps(cabins, cls=DjangoJSONEncoder) for category, cabins in cabins_by_category.items()}

    prices_by_cruise = {}
    for crucero in cruceros_misma_categoria:
        total_price = (getattr(crucero, priceVariable) + tax_total) / total_pasajeros
        prices_by_cruise[crucero.id] = round(total_price, 2)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {
            'fare_prices': fare_prices,
            'available_cabins': all_cabinas,
            'selected_fare_desc': selected_fare_desc,
            'precio_min_inside': precio_min_inside,
            'precio_min_oceanview': precio_min_oceanview,
            'precio_min_balcon': precio_min_balcon,
            'precio_min_suite': precio_min_suite,
            'precio_min_yachtclub': precio_min_yachtclub,
            'ship_names': ship_names,
            'categoria_codes': categoria_codes,
            'prices_by_cruise': prices_by_cruise,
        }
        return JsonResponse(context, encoder=DjangoJSONEncoder)

    context = {
        'fare_prices': fare_prices,
        'available_cabins': all_cabinas,
        'selected_fare_desc': selected_fare_desc,
        'precio_min_inside': precio_min_inside,
        'precio_min_oceanview': precio_min_oceanview,
        'precio_min_balcon': precio_min_balcon,
        'precio_min_suite': precio_min_suite,
        'precio_min_yachtclub': precio_min_yachtclub,
        'ship_names': ship_names,
        'categoria_codes': categoria_codes,
        # Otros datos relevantes...
    }
    return render(request, 'experience.html', context)



def experience1(request, crucero_id, priceVariable):
    logger = logging.getLogger('django')

    crucero = Cruise.objects.filter(cruiseID=crucero_id, nowAvailable="True").exclude(**{priceVariable: None})

    if not crucero:
        return render(request, 'error.html', {'message': 'Crucero no encontrado.'})

    total_pasajeros = obtener_numero_pasajeros(priceVariable)

    selected_fare_desc = None
    if request.GET.get('cruise_only'):
        selected_fare_desc = "ESCAPE TO SEA CRUISE ONLY"
    elif request.GET.get('wifi_included'):
        selected_fare_desc = "DRINKS WIFI OBC INCLUDED"
    elif request.GET.get('winter_sale'):
        selected_fare_desc = "WINTER SALE"
    elif request.GET.get("cruise_with_drinks"):
        selected_fare_desc = "CRUISE WITH DRINKS INCLUDED"
    elif request.GET.get("flash_sale_drinks"):
        selected_fare_desc = "FLASH SALE DRINKS"
    elif request.GET.get("flash_sale_cruise_only"):
        selected_fare_desc = "FLASH SALE CRUISE ONLY"

    if not selected_fare_desc:
        if crucero.exists():
            cruise_only_option = crucero.filter(fareDesc="ESCAPE TO SEA CRUISE ONLY").first()
            if cruise_only_option:
                selected_fare_desc = "ESCAPE TO SEA CRUISE ONLY"
            else:
                for c in crucero:
                    if c.fareDesc != 'WINTER SALE':
                        selected_fare_desc = c.fareDesc
                        break
        else:
            selected_fare_desc = None

    cruceros_misma_categoria = crucero.filter(fareDesc=selected_fare_desc) if selected_fare_desc else crucero

    if not cruceros_misma_categoria:
        return render(request, 'error.html', {'message': 'No hay cruceros disponibles para la tarifa seleccionada.'})

    fare_descs = list(set(crucero.fareDesc for crucero in crucero))

    all_attributes = {}
    crucero1 = cruceros_misma_categoria.first()
    for attr in dir(crucero1):
        try:
            value = getattr(crucero1, attr)
            if not callable(value) and not isinstance(value, models.Manager) and not attr.startswith("__"):
                all_attributes[attr] = value
        except AttributeError:
            continue

    price = getattr(crucero1, priceVariable, None)
    if price is None:
        return render(request, 'error.html', {'message': 'Precio no disponible para esta configuración de pasajeros.'})

    fare_descriptions = [
        "ESCAPE TO SEA CRUISE ONLY",
        "DRINKS WIFI OBC INCLUDED",
        "WINTER SALE",
        "CRUISE WITH DRINKS INCLUDED",
        "FLASH SALE DRINKS",
        "FLASH SALE CRUISE ONLY"
    ]

    fare_prices = {}

    cruise_only_fare = crucero.filter(fareDesc="ESCAPE TO SEA CRUISE ONLY").first()
    flash_cruise_only_fare = crucero.filter(fareDesc="FLASH SALE CRUISE ONLY").first()

    price_cruise_only = Decimal('0')
    price_flash_cruise_only = Decimal('0')

    if cruise_only_fare:
        price_cruise_only = getattr(cruise_only_fare, priceVariable, Decimal('0'))

    if flash_cruise_only_fare:
        price_flash_cruise_only = getattr(flash_cruise_only_fare, priceVariable, Decimal('0'))

    for fare_desc in fare_descriptions:
        fare_key = fare_desc.replace(" ", "_")
        crucero_fare = crucero.filter(fareDesc=fare_desc).first()

        if crucero_fare:
            price_fare = getattr(crucero_fare, priceVariable, Decimal('0'))
        else:
            price_fare = Decimal('0')

        fare_prices[fare_key] = (price_fare - price_cruise_only - price_flash_cruise_only) / total_pasajeros if total_pasajeros > 0 else Decimal('0')


    gftA = all_attributes.get('gftA', Decimal('0'))
    tax_total = total_pasajeros * gftA
    total = tax_total + price
    total_person = total / total_pasajeros


    ship_names = [crucero.shipName for crucero in cruceros_misma_categoria]
    categoria_codes = [extraer_categoria(crucero.category) for crucero in cruceros_misma_categoria]

    if check_cruise():
        cruise_msc()
        return HttpResponse("")

    itinerario = Itinerary.objects.filter(cruise_id=crucero1.cruiseID, itinerary_cd=crucero1.itinCd)

    previous_port = None
    for itinerary in itinerario:
        itinerary.new_day = (previous_port != itinerary.arrival_port)
        previous_port = itinerary.arrival_port

    context = {}

    categoria_codes_mapeados = []
    for code in categoria_codes:
        codigo_mapeado = obtener_codigo_alternativo(code, ship_names[0])
        categoria_codes_mapeados.append(codigo_mapeado)


    experiencia = cabinDetail.objects.filter(
        ship_name__in=ship_names,
        category_code__in=categoria_codes_mapeados,

    ).filter(
        Q(category_code__in=categoria_codes_mapeados) | Q(cabin_number__startswith='G00000')
    )


    all_cabinas = []

    def fetch_cabins_for_category(category):
        cache_key = f"cabins_{crucero1.cruiseID}_{category}"
        cached_cabins = cache.get(cache_key)

        if cached_cabins:
            print(f"Usando caché para la categoría {category}")
            return cached_cabins

        password_hash = calcula_hash_sha256("Mscx1x2x3!")
        cabin_headers = {
            'Content-Type': 'text/xml',
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': password_hash,
            'AgentID': 'US159929',
        }

        cabin_xml_data = f'''
            <DtsCruiseCabinAvailabilityRequest xmlns="DTS">
                <BookingContext>
                    <AdvertisingSource />
                    <BookingContactName>1</BookingContactName>
                    <LoyalityCardMemberLevel />
                    <NoAdults>{total_pasajeros}</NoAdults>
                    <BookingChannel>XML</BookingChannel>
                </BookingContext>
                <CruiseComponent>
                    <CruiseID>{crucero1.cruiseID}</CruiseID>
                    <CategoryCode>{category}</CategoryCode>
                    <PromotionCode></PromotionCode>
                </CruiseComponent>
            </DtsCruiseCabinAvailabilityRequest>
        '''

        try:
            response = requests.post(
                'https://wsrv3.msccruises.com/mscbee/services/cabin/getcabins/',
                headers=cabin_headers,
                data=cabin_xml_data.encode('utf-8')
            )
            response.raise_for_status()

            root = ET.fromstring(response.content)
            ns = {'DTS': 'DTS'}

            available_cabins = root.findall('.//DTS:AvailableCabin', namespaces=ns)

            cabinas = []
            for cabin in available_cabins:
                cabin_number = cabin.find('DTS:CabinNo', namespaces=ns).text
                cabinas.append({
                    "cabin_number": cabin_number,
                    "category_code": category,
                })

            cache.set(cache_key, cabinas, timeout=600)

            print(f"Cabinas disponibles obtenidas para la categoría {category}:")
            for cabin in cabinas:
                print(f"Category: {cabin['category_code']} - Cabin Number: {cabin['cabin_number']}")

            return cabinas

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener cabinas disponibles para la categoría {category}: {str(e)}")
            return []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_cabins_for_category, categoria_codes)
    for result in results:
        all_cabinas.extend(result)

    context['available_cabins'] = all_cabinas

    cabinas_disponibles_api = {cabin['cabin_number'] for cabin in all_cabinas}

    experiencia_por_categoria = {}

    for cabina in all_cabinas:
        if cabina["cabin_number"] == "G00000":
            if cabina["category_code"] not in experiencia_por_categoria:
                experiencia_por_categoria[cabina["category_code"]] = []
            experiencia_por_categoria[cabina["category_code"]].append({
                "ship_name": cabina.get("ship_name", "Unknown"),
                "category_code": cabina["category_code"],
                "category_desc": cabina.get("category_desc", "Unknown"),
                "cabin_number": cabina["cabin_number"],
            })

    for exp in experiencia:
        if exp.cabin_number in cabinas_disponibles_api:
            if exp.category_code not in experiencia_por_categoria:
                experiencia_por_categoria[exp.category_code] = []
            experiencia_por_categoria[exp.category_code].append({
                "ship_name": exp.ship_name,
                "category_code": exp.category_code,
                "category_desc": exp.category_desc,
                "cabin_number": exp.cabin_number,
            })

    experiencia_por_categoria_random = {}
    for category, details in experiencia_por_categoria.items():
        experiencia_por_categoria_random[category] = random.choice(details) if details else None

    context['experiencia_por_categoria'] = experiencia_por_categoria
    context['experiencia_por_categoria_random'] = experiencia_por_categoria_random

    experiencia_por_categoria_json = {category: json.dumps(details, cls=DjangoJSONEncoder) for category, details in experiencia_por_categoria.items()}

    items_por_categoria = {}
    crucero_data = []
    codigos_items = []
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)
        logger.debug(f"Crucero ID: {crucero.id}, Fare Code: {crucero.fareCode}, Categoría: {categoria}, Códigos de Ítems: {codigos_items}")

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_categoria[categoria] = items_list
        crucero_data.append({
            'id': crucero.id,
            'fare_code': crucero.fareCode,
            'categoria': categoria,
            'codigos_items': codigos_items,
            'items': items_list
        })

    items_por_crucero_categoria = {}
    keywords = ['oneAdult', 'twoAdult', 'threeAdult', 'fourAdult']
    for crucero in cruceros_misma_categoria:
        categoria = extraer_categoria(crucero.category)
        codigos_items = obtener_codigos_items(crucero.items, categoria)

        items = Item.objects.filter(fare_code=crucero.fareCode, category=categoria, item_code__in=codigos_items)
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', priceVariable) for keyword in keywords):
            items = items.exclude(item_description='MINORS PACKAGE')

        items_list = list(items.values())
        items_por_crucero_categoria[crucero.id] = {
            'categoria': categoria,
            'items': items_list,
            'codigos_items': codigos_items,
            'fare_code': crucero.fareCode,
            'id': crucero.id
        }
        crucero.categoria_extraida = categoria

    grouped_cruceros = {}

    for crucero in cruceros_misma_categoria:
        categoria_mapeada = obtener_codigo_alternativo(crucero.categoria_extraida, crucero.shipName)

        first_letter = categoria_mapeada[0].upper()

        if first_letter not in grouped_cruceros:
            grouped_cruceros[first_letter] = []

        grouped_cruceros[first_letter].append(crucero)

    precios_inside = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('I') and getattr(crucero, priceVariable) is not None]
    precio_min_inside = min(precios_inside) if precios_inside else None

    precios_oceanview = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('O') and getattr(crucero, priceVariable) is not None]
    precio_min_oceanview = min(precios_oceanview) if precios_oceanview else None

    precios_balcon = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('B') and getattr(crucero, priceVariable) is not None]
    precio_min_balcon = min(precios_balcon) if precios_balcon else None

    precios_suite = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('S') and getattr(crucero, priceVariable) is not None]
    precio_min_suite = min(precios_suite) if precios_suite else None

    precios_yachtclub = [getattr(crucero, priceVariable) for crucero in cruceros_misma_categoria if crucero.categoria_extraida.startswith('Y') and getattr(crucero, priceVariable) is not None]
    precio_min_yachtclub = min(precios_yachtclub) if precios_yachtclub else None

    def format_time_24_to_12(time_str):
        """Convierte el formato de hora de 24 horas a 12 horas con AM/PM"""
        try:
            if not time_str:
                return ""
            time_obj = datetime.strptime(time_str, "%H%M")
            return time_obj.strftime("%I:%M %p").lstrip('0').replace(' 0', ' ')
        except ValueError:
            return time_str

    itinerario_reorganizado = []
    for idx, item in enumerate(itinerario):
        if item.departure_port_name == "At Sea":
            time_str = ""
        else:
            prev_item = itinerario[idx - 1] if idx > 0 else None
            current_item = item

            prev_arrival_time = format_time_24_to_12(prev_item.arrival_time) if prev_item else ""
            current_departure_time = format_time_24_to_12(current_item.departure_time)

            if prev_arrival_time and current_departure_time:
                time_str = f"{prev_arrival_time} — {current_departure_time}"
            elif prev_arrival_time:
                time_str = f"{prev_arrival_time}"
            elif current_departure_time:
                time_str = f"{current_departure_time}"
            else:
                time_str = ""

        itinerario_reorganizado.append({
            'dia': idx + 1,
            'port_name': item.departure_port_name,
            'time': time_str
        })

    if itinerario.exists():
        ultimo_item = itinerario.last()
        if ultimo_item.arrival_port_name == "At Sea":
            time_str = ""
        else:
            time_str = format_time_24_to_12(ultimo_item.arrival_time)

        itinerario_reorganizado.append({
            'dia': len(itinerario) + 1,
            'port_name': ultimo_item.arrival_port_name,
            'time': time_str
        })

    cabins_by_category = {}
    for cabin in all_cabinas:
        category = cabin['category_code']
        if category not in cabins_by_category:
            cabins_by_category[category] = []
        cabins_by_category[category].append(cabin['cabin_number'])

    cabins_by_category_json = {category: json.dumps(cabins, cls=DjangoJSONEncoder) for category, cabins in cabins_by_category.items()}

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'fare_desc': selected_fare_desc,
            'fare_prices': fare_prices,
            'cabinas': [{'cabin_number': cabin['cabin_number'], 'category_desc': cabin['category_desc']} for cabin in cruceros_misma_categoria.values('category', 'cabin_number', 'category_desc')],
        })
    context = {
        'fare_prices': fare_prices,
        'available_cabins': cabins_by_category,
        'experiencia_por_categoria_json': cabins_by_category_json,
        'itinerario_reorganizado': itinerario_reorganizado,
        'crucero': crucero,
        'precio_min_inside': precio_min_inside,
        'precio_min_oceanview': precio_min_oceanview,
        'precio_min_balcon': precio_min_balcon,
        'precio_min_suite': precio_min_suite,
        'precio_min_yachtclub': precio_min_yachtclub,
        'experiencia_por_categoria_json': experiencia_por_categoria_json,
        'cruceros_misma_categoria': cruceros_misma_categoria,
        'grouped_cruceros': grouped_cruceros,
        'experiencia': experiencia,
        'experiencia_por_categoria': experiencia_por_categoria_random,
        'itinerario': itinerario,
        'price_variable': priceVariable,
        'price': price,
        'all_attributes': all_attributes,
        'items_por_crucero_categoria': items_por_crucero_categoria,
        'items_por_categoria': items_por_categoria,
        'codigos_items': codigos_items,
        'categoria_codes': categoria_codes,
        'crucero_data': crucero_data,
        'total_pasajeros': total_pasajeros,
        'total_person': round(price / total_pasajeros, 2) if total_pasajeros else 0,
        'fare_descs': fare_descs,
        'fare_desc': crucero1.fareDesc if crucero1 else None,
        'crucero1': crucero1,
    }

    logger.debug(f"Contexto: {context}")


    return render(request, 'experience1.html', context)



from django.forms import formset_factory
from .forms import PassengerForm
from django.db.models import Q


def cruise_id_to_date(cruise_id):
    match = re.search(r"(\d{4})(\d{2})(\d{2})", cruise_id)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    else:
        return None


def extract_number_of_travelers(price_variable):
    mapping = {
        'oneAdult': (1, 0, 0),
        'twoAdult': (2, 0, 0),
        'threeAdult': (3, 0, 0),
        'fourAdult': (4, 0, 0),
        'twoAdult1Ch': (2, 1, 0),
        'twoAdult2Ch': (2, 2, 0),
        'oneAdult1Ch': (1, 1, 0),
        'oneAdult1JrCh': (1, 0, 1),
        'twoAdult1JrCh': (2, 0, 1),
        'twoAdult1Ch1JrCh': (2, 1, 1),
        'twoAdult2JrCh': (2, 0, 2),
    }
    return mapping.get(price_variable, (0, 0, 0))

def clean_data(data_list):
    return ','.join(data_list)


from datetime import date


def validate_first_passenger_age(first_form):
    date_of_birth = first_form.cleaned_data.get('date_of_birth')
    if date_of_birth:
        today = date.today()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < 21:
            return "The first passenger must be over 21 years old to book."
    return None


def validate_other_passengers(forms, adults, children, junior_children):
    errors = []
    for i, form in enumerate(forms[1:], start=2):
        date_of_birth = form.cleaned_data.get('date_of_birth')
        if date_of_birth:
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))

            if i <= adults:
                if age < 18:
                    errors.append(f"Passenger {i} must be over 18 years old.")
            elif i <= adults + children:
                if age >= 17 or age <= 1:
                    errors.append(f"Child {i - adults} must be younger than 17 years old and older than 1 year.")
            elif i <= adults + children + junior_children:
                if age >= 17 or age <= 1:
                    errors.append(f"Junior child {i - adults - children} must be younger than 17 years old and older than 1 year.")
    return errors


def categorizar_cabinas_pro(category_list):
    categorias = {
        'Inside': [],
        'Ocean View': [],
        'Balcon': [],
        'Suite': [],
        'Yacht Club': []
    }

    category_mapping = {
        'I': 'Inside',
        'B': 'Balcon',
        'O': 'Ocean View',
        'S': 'Suite',
        'Y': 'Yacht Club'
    }

    for index, category_code in enumerate(category_list):
        cabin_info = {'number': f"Cabin-{index + 1}", 'category_code': category_code}
        first_letter = category_code[0] if category_code else ''

        if first_letter in category_mapping:
            mapped_category = category_mapping[first_letter]
            categorias[mapped_category].append(cabin_info)

    categorias = {cat: cabins for cat, cabins in categorias.items() if cabins}
    return categorias




def get_items_por_categoria_pro(fare_code, category, itemcode_list):
    items = Item.objects.filter(fare_code=fare_code, category=category, item_code__in=itemcode_list)
    return items




import xml.etree.ElementTree as ET

def parse_xml(response_content):
    root = ET.fromstring(response_content)
    ns = {'dts': 'DTS'}

    booking_info = {
        'booking_no': root.find('dts:BookingContext/dts:BookingNo', ns).text,
        'agency_id': root.find('dts:BookingContext/dts:AgencyID', ns).text,
        'agent_id': root.find('dts:BookingContext/dts:AgentID', ns).text,
        'booking_currency': root.find('dts:BookingContext/dts:BookingCurrencyCode', ns).text,
        'total_net_price': root.find('dts:BookingInfo/dts:BookingCharges/dts:TotalNetPrice', ns).text,
        'deposit_due_date': root.find('dts:BookingInfo/dts:BookingCharges/dts:DepositDueDate', ns).text,
        'final_payment_date': root.find('dts:BookingInfo/dts:BookingCharges/dts:FinalPaymentDate', ns).text,
        'charges': []
    }

    for charge in root.findall('dts:ChargeDetails/dts:ChargesForComponent', ns):
        booking_info['charges'].append({
            'person_no': charge.find('dts:PersonNo', ns).text,
            'charge_type': charge.find('dts:ChargeTypeCode', ns).text,
            'charge_desc': charge.find('dts:ChargeDesc', ns).text,
            'gross_amount': charge.find('dts:GrossChargeAmount', ns).text
        })

    return booking_info



def extract_gross_charge_details(response_content):
    namespaces = {'dts': 'DTS'}
    root = ET.fromstring(response_content)

    charge_details = {}
    booking_charges = Decimal('0.00')
    deposit_amount_due = Decimal('0.00')
    final_payment_date = ""
    deposit_due_date = ""
    total_payments_received = Decimal('0.00')

    for charge in root.findall('.//dts:ChargesForComponent', namespaces=namespaces):
        person_no = charge.find('dts:PersonNo', namespaces=namespaces).text
        charge_type = charge.find('dts:ChargeTypeCode', namespaces=namespaces).text
        charge_desc = charge.find('dts:ChargeDesc', namespaces=namespaces).text
        gross_charge_amount_text = charge.find('dts:GrossChargeAmount', namespaces=namespaces).text

        gross_charge_amount = Decimal(gross_charge_amount_text) if gross_charge_amount_text else Decimal('0.00')

        if person_no not in charge_details:
            charge_details[person_no] = {
                'details': [],
                'total': Decimal('0.00'),
                'rowspan': 1
            }

        charge_details[person_no]['details'].append({
            'type': charge_type,
            'desc': charge_desc,
            'amount': gross_charge_amount
        })

        charge_details[person_no]['total'] += gross_charge_amount
        charge_details[person_no]['rowspan'] += 1

    booking_charges_element = root.find('.//dts:BookingCharges/dts:BookingCharges', namespaces=namespaces)
    if booking_charges_element is not None and booking_charges_element.text:
        booking_charges = Decimal(booking_charges_element.text)

    deposit_amount_due_element = root.find('.//dts:BookingCharges/dts:DepositAmountDue', namespaces=namespaces)
    if deposit_amount_due_element is not None and deposit_amount_due_element.text:
        deposit_amount_due = Decimal(deposit_amount_due_element.text)

    final_payment_date_element = root.find('.//dts:BookingCharges/dts:FinalPaymentDate', namespaces=namespaces)
    if final_payment_date_element is not None and final_payment_date_element.text:
        final_payment_date = final_payment_date_element.text

    deposit_due_date_element = root.find('.//dts:BookingCharges/dts:DepositDueDate', namespaces=namespaces)
    if deposit_due_date_element is not None and deposit_due_date_element.text:
        deposit_due_date = deposit_due_date_element.text

    total_payments_received_element = root.find('.//dts:BookingCharges/dts:TotalPaymentsReceived', namespaces=namespaces)
    if total_payments_received_element is not None and total_payments_received_element.text:
        total_payments_received = Decimal(total_payments_received_element.text)

    return (charge_details, booking_charges, deposit_amount_due,
            final_payment_date, deposit_due_date, total_payments_received)

def format_date(date_str):
    if not date_str:
        return ""
    try:
        date_str = ' '.join(date_str.split()[:4] + date_str.split()[5:])
        date_obj = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
        return date_obj.strftime("%B %d, %Y")
    except ValueError:
        return date_str




def save_invoice_customer_data(user, data):
    invoice = InvoiceCustomer(
        user=user,
        booking_context=data.get('booking_context'),
        passenger_data_json=data.get('passenger_data_json'),
        xml_data=data.get('xml_data'),
        response_content=data.get('response_content'),
        cruise=data.get('cruise'),
        cabin_number=data.get('cabin_number'),
        itemtype_list=data.get('itemtype_list'),
        itemcode_list=data.get('itemcode_list'),
        packagecode_list=data.get('packagecode_list'),
        category_list=data.get('category_list'),
        booking_no=data.get('booking_no'),
        total=data.get('total'),
        desembarkation_port=data.get('desembarkation_port'),
        embarkation_port=data.get('embarkation_port'),
        total_general=data.get('total_general'),
        crucero=data.get('crucero'),
        metodo_pago=data.get('metodo_pago'),
        moneda=data.get('moneda'),
        fecha_salida=data.get('fecha_salida'),
        fecha_regreso=data.get('fecha_regreso'),
        categoria=data.get('categoria'),
        lock_id=data.get('lock_id'),
        total_travelers=data.get('total_travelers'),
        price_variable=data.get('price_variable'),
        precio=data.get('precio'),
        charge_details=data.get('charge_details'),
        booking_charges=data.get('booking_charges'),
        deposit_amount_due=data.get('deposit_amount_due'),
        final_payment_date=data.get('final_payment_date'),
        deposit_due_date=data.get('deposit_due_date'),
        total_payments_received=data.get('total_payments_received'),
        debug_info=data.get('debug_info'),
        crucero_fields=data.get('crucero_fields'),
        one_pax=data.get('one_pax'),
        two_pax=data.get('two_pax'),
        three_pax=data.get('three_pax'),
        four_pax=data.get('four_pax'),
        cabin_categories=data.get('cabin_categories'),
        items_por_categoria=data.get('items_por_categoria'),
        return_date=data.get('returnDate'),
        charges=data.get('charges'),
        current_datetime=data.get('current_datetime'),
        passenger_data=data.get('passenger_data'),
        additional_charges_sum=data.get('additional_charges_sum'),
    )
    invoice.save()



def serialize_crucero(crucero):
    crucero_dict = {}
    for k, v in crucero.__dict__.items():
        if isinstance(v, date):
            crucero_dict[k] = v.strftime('%Y-%m-%d')
        elif isinstance(v, (int, float, str, bool)) or v is None:
            crucero_dict[k] = v
    return json.dumps(crucero_dict)

from django.core.exceptions import ValidationError



def get_states(request):
    if request.method == 'GET':
        states = State.objects.all().values('code', 'name')
        return JsonResponse(list(states), safe=False)

def get_cities(request, state_name):
    cities = City.objects.filter(city_name__icontains=state_name).values('city_code', 'city_name')
    return JsonResponse(list(cities), safe=False)



def bookingpro(request, cruise_id, price_variable, cabin_number, priceType, fareCode):
    cruise_date = cruise_id_to_date(cruise_id)

    itemcode_list = request.GET.getlist('itemcode')
    itemtype_list = request.GET.getlist('itemtype')
    packagecode_list = request.GET.getlist('packagecode')
    category_list = request.GET.getlist('category')
    categoria = category_list[0] if category_list else None

    current_datetime = datetime.now().strftime('%B %d, %Y')


    items_list = []
    if itemcode_list:
        items_list = list(
            Item.objects.filter(item_code__in=itemcode_list)
                .only('item_code')
                .values_list('item_code', flat=True)
                .distinct()
        )

    print(items_list)


    request.session['items_list'] = items_list
    request.session['itemtype_list'] = itemtype_list

    print(itemcode_list)
    print(items_list)
    if not categoria:
        return render(request, 'booking_error.html', {'mensaje_error': 'Categoría no especificada.'})

    crucero = Cruise.objects.filter(
        cruiseID=cruise_id,
        fareCode=fareCode,
        category__in=category_list
    ).exclude(
        **{f'{price_variable}__isnull': True}
    ).first()

    if not crucero:
        return render(request, 'booking_error.html', {'mensaje_error': 'Crucero no encontrado.'})

    itinerario = Itinerary.objects.filter(cruise_id=crucero.cruiseID, itinerary_cd=crucero.itinCd)

    if crucero:
        request.session['crucero'] = {
            'shipName': crucero.shipName,
            'itinDesc': crucero.itinDesc,
            'sailingDate': crucero.sailingDate.strftime('%Y-%m-%d'),
            'returnDate': (crucero.sailingDate + timedelta(days=crucero.nights)).strftime('%Y-%m-%d'),
            'itinCd': crucero.itinCd,
        }
    else:
        request.session['crucero'] = None


    experiencia_query = Item.objects.filter(
        item_code__in=itemcode_list, fare_code=fareCode
    ).values_list('item_description', 'item_description_long')

    experiencia_list = [
        (item[0], item[1].capitalize() if item[1] else '')
        for item in experiencia_query]
    experiencia_list = list(set(experiencia_list))

    name_experience = [item[0] for item in experiencia_list]

    request.session['name_experience'] = name_experience

    print(experiencia_list)

    request.session['experiencia_list'] = experiencia_list

    precio = getattr(crucero, price_variable, None)
    adults, children, junior_children = extract_number_of_travelers(price_variable)
    total_travelers = adults + children + junior_children
    cabin_categories = categorizar_cabinas_pro(category_list)

    request.session['total_travelers'] = total_travelers
    request.session['cabin_categories'] = cabin_categories

    if price_variable == 'oneAdult':
        one_pax = precio
        two_pax = 0
        three_pax = 0
        four_pax = 0
    elif price_variable == 'twoAdult':
        one_pax = precio / 2 if adults > 0 else 0
        two_pax = precio / 2 if adults > 1 else 0
        three_pax = 0
        four_pax = 0
    elif price_variable == 'oneAdult1Ch':
        one_pax = precio / 2 if adults > 0 else 0
        two_pax = precio / 2 if children > 0 else 0
        three_pax = 0
        four_pax = 0
    elif price_variable == 'threeAdult':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) if adults > 2 else 0
        four_pax = 0
    elif price_variable == 'fourAdult':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) / 2 if adults >= 2 else 0
        four_pax = (precio - crucero.twoAdult) / 2 if adults > 3 else 0
    elif price_variable == 'twoAdult1Ch':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) if children > 0 else 0
        four_pax = 0
    elif price_variable == 'twoAdult2Ch':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) / 2 if children > 0 else 0
        four_pax = (precio - crucero.twoAdult) / 2 if children > 1 else 0
    elif price_variable == 'twoAdult1Ch1JrCh':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) / 2 if children > 0 else 0
        print(one_pax, two_pax, three_pax)
        four_pax = (precio - crucero.twoAdult) / 2 if junior_children > 0 else 0
    elif price_variable == 'twoAdult1JrCh':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) / 2 if junior_children > 0 else 0
        four_pax = 0
    elif price_variable == 'twoAdult2JrCh':
        one_pax = crucero.twoAdult / 2 if adults > 0 else 0
        two_pax = crucero.twoAdult / 2 if adults > 1 else 0
        three_pax = (precio - crucero.twoAdult) / 2 if junior_children > 0 else 0
        four_pax = (precio - crucero.twoAdult) / 2 if junior_children > 1 else 0
    else:
        one_pax, two_pax, three_pax, four_pax = 0, 0, 0, 0

    tax_per_person = crucero.gftA
    total_one_pax = one_pax + tax_per_person if one_pax > 0 else Decimal('0.00')
    total_two_pax = two_pax + tax_per_person if two_pax > 0 else Decimal('0.00')
    if price_variable in ['twoAdult1JrCh', 'threeAdult', 'twoAdult1Ch', 'twoAdult2Ch', 'twoAdult2JrCh', 'fourAdult', 'twoAdult1Ch1JrCh']:
        total_three_pax = three_pax + tax_per_person if three_pax >= 0 else Decimal('0.00')
    else:
        total_three_pax = Decimal('0.00')

    if price_variable in ['twoAdult2JrCh', 'twoAdult1Ch1JrCh', 'twoAdult2Ch', 'fourAdult']:
        total_four_pax = four_pax + tax_per_person if four_pax >= 0 else Decimal('0.00')
    else:
        total_four_pax = Decimal('0.00')

    total_general = total_one_pax + total_two_pax + total_three_pax + total_four_pax

    PassengerFormSet = formset_factory(PassengerForm, extra=total_travelers)
    formset = PassengerFormSet(request.POST or None)


    password_hash = calcula_hash_sha256("Mscx1x2x3!")
    url = 'https://wsrv3.msccruises.com/mscbee/services/cruise/diningresavail'
    headers = {
        'Content-Type': 'text/xml',
        'AgencyID': 'US159929',
        'True-Client-IP': '10.0.0.50',
        'UserID': 'OTA3-US159929',
        'Password': password_hash,
        'AgentID': 'US159929',
        }
    xml_data = f'''<DtsDiningResidualAvailabilityRequest
    xmlns="DTS">
        <CruiseId>{crucero.cruiseID}</CruiseId>
        <CategoryCode>{categoria}</CategoryCode>
        <BookingChannel>XML</BookingChannel>
        <NoPassengers>{total_travelers}</NoPassengers>
    </DtsDiningResidualAvailabilityRequest>'''
    try:
        response = requests.post(url, headers=headers, data=xml_data.encode('utf-8'))
        response.raise_for_status()
        dining_response_content = response.content.decode('utf-8')

        root = ET.fromstring(dining_response_content)
        namespace = {'DTS': 'DTS'}

        dining_options = []

        for dining_detail in root.findall('.//DTS:DiningDetail', namespaces=namespace):
            availability = int(dining_detail.find('DTS:Availability', namespaces=namespace).text)
            dining_description = dining_detail.find('DTS:DiningDescription', namespaces=namespace).text

            if availability >= total_travelers and dining_description:
                dining_options.append(dining_description)
        print(dining_response_content)

    except requests.exceptions.RequestException as e:
        dining_response_content = f"Error during API request: {str(e)}"
        dining_options = []


    if request.method == 'POST':
        if formset.is_valid():
            passenger_data = []
            address = ''
            zipcode = ''
            hidden_value = request.POST.get('hidden_value')
            request.session['dining'] = hidden_value
            state_province = ''
            for idx, form in enumerate(formset):
                if form.cleaned_data:
                    country_code = request.POST.get('country_code')
                    dining_room = request.POST.get('dining_option')
                    passenger_info = {
                        'city': form.cleaned_data.get('city', ''),
                        'date_of_birth': form.cleaned_data.get('date_of_birth', '').strftime('%Y-%m-%d'),
                        'telephone_no': form.cleaned_data.get('telephone_no', ''),
                        'email': form.cleaned_data.get('email', ''),
                        'gender': form.cleaned_data.get('gender', ''),
                        'last_name': form.cleaned_data.get('last_name', ''),
                        'first_name': form.cleaned_data.get('first_name', ''),
                        'address': form.cleaned_data.get('address', '') if idx == 0 else '',
                        'zipcode': form.cleaned_data.get('zipcode', '') if idx == 0 else '',
                        'state_province': form.cleaned_data.get('state_province', '') if idx == 0 else '',
                        'dining': hidden_value if idx == 0 else '',
                    }
                    if idx == 0:
                        address = form.cleaned_data.get('address', '')
                        zipcode = form.cleaned_data.get('zipcode', '')
                        state_province = form.cleaned_data.get('state_province', '')

                    passenger_data.append(passenger_info)

            if len(passenger_data) != total_travelers:
                return render(request, 'booking_error.html', {
                    'mensaje_error': 'Número de pasajeros no coincide con los datos proporcionados.',
                })
            request.session['passenger_data'] = passenger_data
            request.session['address'] = address
            request.session['zipcode'] = zipcode
            request.session['state_province'] = state_province
            passenger_data_json = json.dumps(passenger_data, indent=4)
            dining_value = request.session.get('dining', 'default_value')

            print(f"El valor de dining_value es: {dining_value}")

            password_hash = calcula_hash_sha256("Mscx1x2x3!")
            url = 'https://wsrv3.msccruises.com/mscbee/services/booking/bookRequestV1/'
            headers = {
                'Content-Type': 'text/xml',
                'AgencyID': 'US159929',
                'True-Client-IP': '10.0.0.50',
                'UserID': 'OTA3-US159929',
                'Password': password_hash,
                'AgentID': 'US159929',
            }

            participant_data_xml = ''
            for i, pdata in enumerate(passenger_data, start=1):
                participant_data_xml += f'''
                <ParticipantData>
                    <PersonNo>{i}</PersonNo>
                    <LastName>{pdata['last_name']}</LastName>
                    <FirstName>{pdata['first_name']}</FirstName>
                    <PersonType>A</PersonType>
                    <DateOfBirth>{pdata['date_of_birth']}</DateOfBirth>
                    <Greeting/>
                    <PlaceOfBirth/>
                    <CountryOfBirth>{pdata['city']}</CountryOfBirth>
                    <Gender>{pdata['gender']}</Gender>
                    <LanguageCode/>
                    <NationalityCode/>
                    <FrequentTravelerNumber/>
                    <PassportData>
                        <PersonNo>{i}</PersonNo>
                    </PassportData>
                    <InsuranceInformation>
                        <CompanyName/>
                        <PolicyNumber/>
                        <CompanyPhNo>3054282518</CompanyPhNo>
                    </InsuranceInformation>
                    <ParticipantAddress>
                        <PAXAddressLine1>{address}</PAXAddressLine1>
                        <PAXCity>{pdata['city']}</PAXCity>
                        <PAXEmail>thatvacationtravel@gmail.com</PAXEmail>
                        <PAXPrefCellular>+{country_code}</PAXPrefCellular>
                        <PAXCellular>3054282518</PAXCellular>
                        <PAXCountryCode>{pdata['city']}</PAXCountryCode>
                    </ParticipantAddress>
                </ParticipantData>
                '''

            package_item_definitions = ''
            for code, type_, package in zip(itemcode_list, itemtype_list, packagecode_list):
                package_item_definitions += f'''
                <PackageItemDefinition>
                    <PackageCode>{package}</PackageCode>
                    <PackageItemDetails>
                        <ItemType>{type_}</ItemType>
                        <ItemCode>{code}</ItemCode>
                        <StartDate>{cruise_date}</StartDate>
                        <EndDate>{cruise_date}</EndDate>
                        <PersonNo>1,2,3,4</PersonNo>
                    </PackageItemDetails>
                </PackageItemDefinition>
                '''

            xml_data = f'''
            <DtsBookRequestMessageV1 xmlns="DTS">
                <BookingAction>
                    <BookOrQuote>B</BookOrQuote>
                </BookingAction>
                <BookingContext>
                    <AgencyID>US159929</AgencyID>
                    <AgencyReference/>
                    <AgentID>US159929</AgentID>
                    <BookingChannel>XML</BookingChannel>
                    <BookingContactName>Tvacation</BookingContactName>
                    <BookingNo/>
                    <ConsortiumCode/>
                    <BookingCurrencyCode>USD</BookingCurrencyCode>
                    <GroupID/>
                    <LanguageCode>ENG</LanguageCode>
                    <LockBooking/>
                    <MarketCode>USA</MarketCode>
                    <OfficeCode>USA</OfficeCode>
                </BookingContext>
                <ParticipantList>
                    {participant_data_xml}
                </ParticipantList>
                <ComponentsToBook>
                    <ComponentDetails>
                        <ItemType>CRU</ItemType>
                        <ItemCode>{cruise_id}</ItemCode>
                        <CategoryCode>{category_list[0]}</CategoryCode>
                        <PromotionCode>{priceType}</PromotionCode>
                        <PersonNo>1,2,3,4</PersonNo>
                        <CabinNo>{cabin_number}</CabinNo>
                        {package_item_definitions}
                        <Dining>
                            <Room>{dining_value}</Room>
                            <Seating>N</Seating>
                        </Dining>
                    </ComponentDetails>
                </ComponentsToBook>
            </DtsBookRequestMessageV1>
            '''

            response = requests.post(url, headers=headers, data=xml_data.encode('utf-8'))
            response_content = response.content.decode('utf-8', 'ignore')

            if response.status_code == 200:
                cabin_categories = categorizar_cabinas_pro(category_list)
                (charge_details, booking_charges, deposit_amount_due, final_payment_date, deposit_due_date, total_payments_received) = extract_gross_charge_details(response_content)
                final_payment_date_formatted = format_date(final_payment_date)
                deposit_due_date_formatted = format_date(deposit_due_date)
                root = ET.fromstring(response_content)
                namespaces = {'dts': 'DTS'}
                booking_element = root.find(".//dts:BookingNo", namespaces=namespaces)
                total1 = root.find(".//dts:NetBalanceDue", namespaces=namespaces)
                total2 = root.find(".//dts:BookingCharges", namespaces=namespaces)
                metodo_pago1 = root.find(".//dts:PayMethod", namespaces=namespaces)
                moneda1 = root.find(".//dts:BookingCurrencyCode", namespaces=namespaces)
                fecha_salida1 = root.find(".//dts:StartDate", namespaces=namespaces)
                fecha_regreso1 = root.find(".//dts:EndDate", namespaces=namespaces)
                categoria1 = root.find(".//dts:CategoryCode", namespaces=namespaces)
                deposit_amount_due = root.find(".//dts:DepositAmountDue", namespaces=namespaces)

                booking_no = booking_element.text if booking_element is not None else "No encontrado"
                total = total1.text if total1 is not None else "No encontrado"
                total_general = total2.text if total2 is not None else "No encontrado"
                metodo_pago = metodo_pago1.text if metodo_pago1 is not None else "No encontrado"
                moneda = moneda1.text if moneda1 is not None else "No encontrada"
                fecha_salida = fecha_salida1.text if fecha_salida1 is not None else "No encontrada"
                fecha_regreso = fecha_regreso1.text if fecha_regreso1 is not None else "No encontrada"
                categoria = categoria1.text if categoria1 is not None else "No encontrada"
                deposit_amount_due = deposit_amount_due.text if deposit_amount_due is not None else "No encontrado"

                booking_no = booking_element.text if booking_element is not None else None

                crucero_id = crucero.cruiseID if crucero else None
                price_variable = price_variable

                if not booking_no:
                    url = reverse('experience', args=[crucero_id, price_variable])
                    root = ET.fromstring(response_content)
                    namespace = {'ns': 'DTS'}
                    message_text = root.find('.//ns:MessageText', namespace).text

                    full_message = (
                        'Message from ThatVacation: '
                        f'{message_text}. '
                        'Please select another cabin to obtain your booking number confirmation.'
                    )
                    messages.warning(request, full_message)

                    return HttpResponseRedirect(url)

                request.session['passenger_data'] = passenger_data
                request.session['crucero_id'] = crucero.cruiseID
                request.session['fecha_salida'] = crucero.sailingDate.strftime('%Y-%m-%d')
                request.session['user_id'] = request.user.id
                request.session['booking_no'] = booking_no
                request.session['deposit_amount_due'] = deposit_amount_due
                request.session['response_content'] = response_content

                url1 = 'https://wsrv3.msccruises.com/mscbee/services/cabin/getcabinlock/'
                xml_data1 = f'''
                <DtsCruiseCabinLockRequestMessage xmlns="DTS">
                    <CruiseId>{cruise_id}</CruiseId>
                    <CabinsToBook>
                        <CabinNo>{cabin_number}</CabinNo>
                    </CabinsToBook>
                </DtsCruiseCabinLockRequestMessage>
                '''

                response1 = requests.post(url1, headers=headers, data=xml_data1.encode('utf-8'))
                lock_response = response1.content.decode('utf-8', 'ignore')

                root1 = ET.fromstring(lock_response)
                lock_id_element = root1.find('.//dts:LockID', namespaces=namespaces)
                lock_id_element1 = root1.find('.//{DTS}MessageText')

                lock_id = lock_id_element.text if lock_id_element is not None else lock_id_element1.text if lock_id_element1 is not None else "No encontrado"

                desembarkation_port = get_object_or_404(Port, port_code=crucero.sailingPort)
                embarkation_port = get_object_or_404(Port, port_code=crucero.terminationPort)

                passenger_data = request.session.get('passenger_data')
                crucero_id = request.session['cruise_id'] = cruise_id
                fecha_salida = request.session.get('fecha_salida')
                user_id = request.session['user_id'] = request.user.id
                booking_no = request.session.get('booking_no')

                if not passenger_data or not crucero_id or not fecha_salida or not user_id or not booking_no:
                    return render(request, 'error.html', {'mensaje_error': 'Datos de sesión incompletos.'})

                crucero2 = Cruise.objects.filter(cruiseID=cruise_id).first()
                user = User.objects.get(id=user_id)

                for pdata in passenger_data:
                    Booking.objects.get_or_create(
                        user=user,
                        booking_number=booking_no,
                        dining =  request.session.get('dining'),
                        defaults={
                            'email': pdata['email'],
                            'first_name': pdata['first_name'],
                            'last_name': pdata['last_name'],
                            'phone': pdata['telephone_no'],
                            'ship': crucero2.cruiseID,
                            'departure_day': crucero2.sailingDate.strftime('%Y-%m-%d'),
                            'zip_code': pdata.get('Zipcode') or 0,
                            'unique_id': random.randint(1000, 999999999999),
                            'total_to_pay': booking_charges,

                        }
                    )

                    request.session['total_to_pay'] = str(booking_charges)

                charges = []
                for charge in root.findall('.//dts:ChargesForComponent', namespaces=namespaces):
                    charges.append({
                        'person_no': charge.find('dts:PersonNo', namespaces=namespaces).text,
                        'charge_type': charge.find('dts:ChargeTypeCode', namespaces=namespaces).text,
                        'charge_desc': charge.find('dts:ChargeDesc', namespaces=namespaces).text,
                        'gross_amount': charge.find('dts:GrossChargeAmount', namespaces=namespaces).text
                    })

                charge_totals = {}

                for charge in charges:
                    person_no = charge['person_no']
                    charge_type = charge['charge_type']
                    charge_desc = charge['charge_desc']
                    gross_amount_str = charge['gross_amount']

                    try:
                        gross_amount = Decimal(gross_amount_str)
                    except (ValueError, InvalidOperation):
                        gross_amount = Decimal('0.00')

                    if person_no not in charge_totals:
                        charge_totals[person_no] = {
                            'total_cab_srn': 0.00,
                            'details': [],
                            'total': 0.00
                        }

                    if charge_type in ['CAB', 'SRN']:
                        charge_totals[person_no]['total_cab_srn'] += float(gross_amount)

                    charge_totals[person_no]['details'].append({
                        'type': charge_type,
                        'desc': charge_desc,
                        'amount': float(gross_amount)
                    })

                    charge_totals[person_no]['total'] += float(gross_amount)

                additional_charges_sum = 0.00
                for person_no, data in charge_totals.items():
                    additional_charges_sum += data['total_cab_srn']
                request.session['charge_totals'] = charge_totals

        if 'credit_card_number' in request.POST:
            payment_amount1 = Decimal('1.00')
            payment_amount2 = request.POST.get('payment_amount')

            try:
                payment_amount = Decimal(payment_amount1)
            except (InvalidOperation, ValueError):
                payment_amount = Decimal('0.00')

            credit_card_code = request.POST.get('credit_card_code')
            credit_card_number = request.POST.get('credit_card_number')
            name_on_credit_card = request.POST.get('name_on_credit_card')
            ccv_code = request.POST.get('ccv_code')
            expiration_month = request.POST.get('expiration_month')
            expiration_year = request.POST.get('expiration_year')
            booking_no = request.session.get('booking_no')
            address = request.POST.get('address')
            zipcode = request.POST.get('zipcode')
            city = request.POST.get('city')
            state = request.POST.get('state')

            request.session['payment_amount'] = payment_amount


            if request.POST.get('payment_amount'):
                try:
                    payment_amount = Decimal(request.POST.get('payment_amount'))
                    print(f"Payment amount from POST: {payment_amount}")
                except (ValueError, InvalidOperation):
                    payment_amount = Decimal('0.00')
                    print("Invalid payment_amount received, setting to 0.00")

            else:
                print(f"No payment_amount in POST, keeping default: {payment_amount}")

            try:
                booking_charges = Decimal(request.session.get('total_to_pay', '0.00'))
            except (ValueError, InvalidOperation):
                booking_charges = Decimal('0.00')

            request.session['total_to_pay'] = str(booking_charges)
            request.session['payment_amount'] = str(payment_amount)


            if request.user.is_authenticated:
                user = request.user
            else:
                return redirect('login')

            try:
                last_booking = Booking.objects.filter(user=user).latest('id')
            except Booking.DoesNotExist:
                last_booking = None


            if last_booking:
                credit_card_number = request.POST.get('credit_card_number')
                if credit_card_number:
                    last_booking.last_four_digit_card = credit_card_number[-4:]

                last_booking.type_card = request.POST.get('credit_card_code')
                last_booking.card_address = address
                last_booking.zip_code = request.POST.get('zipcode')
                last_booking.city = request.POST.get('city')
                last_booking.country = request.POST.get('country')
                last_booking.state = request.POST.get('state')
                last_booking.total_paid = payment_amount
                last_booking.balance =  booking_charges - payment_amount
                last_booking.last_payment_date = timezone.now()

                print(f"Booking Charges (Total): {booking_charges}")
                print(f"Payment Amount: {payment_amount}")

                balance = booking_charges - payment_amount
                print(f"Calculated Balance: {balance}")

                url = 'https://wsrv.msccruises.com/upp/proxy/push/b5383d345a695897'
            headers = {
                'AgencyID': 'US159929',
                'True-Client-IP': '10.0.0.50',
                'UserID': 'OTA3-US159929',
                'Password': '0cf43a5e90d824440ea9b809b153dcfb4d5960ecb450442c904c1d28b16d8aa0',
                'AgentID': 'US159929',
            }

            xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
                <DtsApplyPaymentRequestMessage xmlns="DTS">
                    <BookingContext>
                        <AgencyID>US159929</AgencyID>
                        <BookingContactName>ThatVacation</BookingContactName>
                        <BookingNo>{booking_no}</BookingNo>
                        <BookingChannel>XML</BookingChannel>
                    </BookingContext>
                    <Payment>
                        <ReceivedFrom>fusco</ReceivedFrom>
                        <PaymentAmount>{payment_amount}</PaymentAmount>
                        <FormOfPaymentCode>CC</FormOfPaymentCode>
                        <DocumentNo/>
                        <ReferenceNo/>
                        <CreditCardInfo>
                            <CreditCardCode>{credit_card_code}</CreditCardCode>
                            <CreditCardNumber>{credit_card_number}</CreditCardNumber>
                            <NameOnCreditCard>{name_on_credit_card}</NameOnCreditCard>
                            <CCVCode>{ccv_code}</CCVCode>
                            <Process>true</Process>
                            <ExpirationDate>
                                <ExpirationMonth>{expiration_month}</ExpirationMonth>
                                <ExpirationYear>{expiration_year}</ExpirationYear>
                            </ExpirationDate>
                            <IssueNum>1</IssueNum>
                        </CreditCardInfo>
                        <ScheduleDue/>
                        <SkipDirecao>true</SkipDirecao>
                    </Payment>
                </DtsApplyPaymentRequestMessage>
            '''

            response = requests.post(url, headers=headers, data=xml_data.encode('utf-8'))
            response_content = response.content.decode('utf-8', 'ignore')

            print(f"Estado de la respuesta HTTP: {response.status_code}")
            print(response_content)

            last_four_digits = credit_card_number[-4:]
            booking_charges_json = request.session.get('booking_charges', '{}')
            try:
                booking_charges_data = json.loads(booking_charges_json)

                if isinstance(booking_charges_data, dict):
                    for key, value in booking_charges_data.items():
                        if isinstance(value, str):
                            try:
                                cleaned_value = value.replace('“', '').replace('”', '').strip('"')
                                booking_charges_data[key] = Decimal(cleaned_value)
                            except (InvalidOperation, ValueError):
                                raise ValidationError(f'El valor "{value}" no es un número decimal válido.')
                        elif isinstance(value, (int, float)):
                            booking_charges_data[key] = Decimal(value)
                else:
                    raise ValidationError('Los datos de "booking_charges" no están en el formato esperado (diccionario).')

            except (json.JSONDecodeError, ValidationError, ValueError, TypeError) as e:
                booking_charges_data = {}

            deposit_amount_due = request.session.get('deposit_amount_due', '0.00')

            cleaned_value = deposit_amount_due.replace('“', '').replace('”', '').strip('"')

            try:
                deposit_amount_due = Decimal(cleaned_value)
            except (InvalidOperation, ValueError):
                raise ValidationError(f'El valor "{deposit_amount_due}" no es un número decimal válido.')

            if response.status_code == 200:
                    namespaces = {'dts': 'DTS'}
                    root = ET.fromstring(response_content)
                    advisory_message = root.find('.//dts:AdvisoryMessage', namespaces)

                    if advisory_message is not None:
                        message_type = advisory_message.find('dts:MessageType', namespaces).text.strip()
                        message_text = advisory_message.find('dts:MessageText', namespaces).text.strip()

                        if message_type == 'F':
                            print(f"Error en el pago: {message_text}")
                            return render(request, 'record_payment_error.html', {
                                'error': f"Error processing the payment: {message_text} Please try again.",
                                'passenger_data':request.session.get('passenger_data'),
                                'charge_totals': request.session.get('charge_totals'),
                                'booking_context': root.iter(),
                                'xml_data': xml_data,
                                'response_content': response_content,
                                'cruise': cruise_id,
                                'cabin_number': cabin_number,
                                'itemtype_list': itemtype_list,
                                'itemcode_list': itemcode_list,
                                'packagecode_list': packagecode_list,
                                'category_list': category_list,
                                'booking_no': booking_no,
                                'total_general': total_general,
                                'crucero': crucero,
                                'categoria': categoria,
                                'total_travelers': total_travelers,
                                'price_variable': price_variable,
                                'precio': precio,
                                'booking_charges': booking_charges,
                                'deposit_amount_due': request.session.get('deposit_amount_due'),
                                'debug_info': {
                                    'cruise_id': cruise_id,
                                    'price_variable': price_variable,
                                    'cabin_number': cabin_number,
                                    'priceType': priceType,
                                    'fareCode': fareCode,
                                    'actual_price_from_model': precio,
                                    'one_pax': one_pax,
                                    'two_pax': two_pax,
                                    'three_pax': three_pax,
                                    'four_pax': four_pax,
                                    'crucero': crucero,
                                    'price_per_adult': precio / adults if adults > 0 else 0,
                                },
                                'crucero_fields': {k: v for k, v in crucero.__dict__.items() if not k.startswith('_')},
                                'one_pax': one_pax,
                                'two_pax': two_pax,
                                'three_pax': three_pax,
                                'four_pax': four_pax,
                                'cabin_categories': cabin_categories,
                                'items_por_categoria': itemcode_list,
                                'returnDate': (crucero.sailingDate + timedelta(days=crucero.nights)).strftime('%Y-%m-%d'),
                                'current_datetime': current_datetime,
                                'experiencia': experiencia_list,

                            })
                    print(f"Pago exitoso para la reserva {booking_no}")

                    last_booking.save()

            print(f"Saved Balance: {last_booking.balance}")
            print(f"Procesando pago para la reserva {booking_no}...")

            xml_content = request.session.get('response_content')
            root = ET.fromstring(xml_content)
            namespace = {'ns': 'DTS'}
            total_comisiones = 0.0
            for charge in root.findall('.//ns:ChargesForComponent', namespace):
                commission_amount = charge.find('ns:StdCommissionAmount', namespace)
                if commission_amount is not None:
                    valor = float(commission_amount.text)
                    if valor != 0:
                        total_comisiones += valor

            booking_info, charge_details = parse_xml_response(xml_content)
            charge_details_json = json.dumps(charge_details, default=str)
            InvoiceCustomer.objects.create(
                user=request.user,
                booking_context=json.dumps(request.session.get('crucero', {})),
                passenger_data_json=json.dumps(request.session.get('passenger_data', {})),
                response_content=response_content,
                cruise=cruise_id,
                desglose_passenger_data=json.dumps({
                    'booking_info': booking_info,
                    'charge_details': charge_details
                }),
                xml_data = ', '.join([desc_long for _, desc_long in experiencia_list if desc_long]) if experiencia_list else 'No experience descriptions',
                crucero_fields = ', '.join(items_list) if items_list else 'No packages included',
                last_four_digits_card = last_four_digits,
                cabin_number=cabin_number,
                itemtype_list=json.dumps(itemtype_list),
                itemcode_list=json.dumps(itemcode_list),
                packagecode_list=json.dumps(packagecode_list),
                category_list=json.dumps(category_list),
                booking_no=booking_no,
                total=total_general,
                desembarkation_port=json.dumps(request.session.get('desembarkation_port', {})),
                embarkation_port=json.dumps(request.session.get('embarkation_port', {})),
                total_general=total_general,
                crucero=crucero.shipName,
                metodo_pago=json.dumps(request.session.get('metodo_pago',{})),
                moneda=json.dumps(request.session.get('moneda',{})),
                fecha_salida=crucero.sailingDate,
                fecha_regreso=crucero.sailingDate + timedelta(days=crucero.nights),
                categoria=categoria,
                lock_id=json.dumps(request.session.get('lock_id', {})),
                total_travelers=total_travelers,
                price_variable=price_variable,
                precio=precio,
                charge_details=json.dumps(request.session.get('charge_details', {})),
                booking_charges=booking_charges_json,
                deposit_amount_due=deposit_amount_due,
                final_payment_date=json.dumps(request.session.get('final_payment_date_formatted', {})),
                deposit_due_date=json.dumps(request.session.get('deposit_due_date_formatted', {})),
                total_payments_received=json.dumps(request.session.get('total_payments_received', {})),
                debug_info=json.dumps({
                    'cruise_id': cruise_id,
                    'price_variable': price_variable,
                    'cabin_number': cabin_number,
                    'priceType': priceType,
                    'fareCode': fareCode,
                    'actual_price_from_model': float(precio) if isinstance(precio, Decimal) else precio,
                    'one_pax': float(one_pax) if isinstance(one_pax, Decimal) else one_pax,
                    'two_pax': float(two_pax) if isinstance(two_pax, Decimal) else two_pax,
                    'three_pax': float(three_pax) if isinstance(three_pax, Decimal) else three_pax,
                    'four_pax': float(four_pax) if isinstance(four_pax, Decimal) else four_pax,
                    'crucero': {
                        'shipName': crucero.shipName,
                        'itinDesc': crucero.itinDesc,
                        'sailingDate': crucero.sailingDate.strftime('%Y-%m-%d'),
                        'nights': crucero.nights,
                    },
                    'price_per_adult': float(precio / adults) if adults > 0 else 0,
                }),

                one_pax=one_pax,
                two_pax=two_pax,
                three_pax=three_pax,
                four_pax=four_pax,
                cabin_categories=json.dumps(cabin_categories),
                items_por_categoria=json.dumps(itemcode_list),
                return_date=(crucero.sailingDate + timedelta(days=crucero.nights)),
                charges=json.dumps(request.session.get('charges', {})),
                current_datetime=datetime.now(),
                passenger_data=json.dumps(request.session.get('passenger_data', {})),
                additional_charges_sum=json.dumps(request.session.get('additional_charges_sum', {})),
                comission = total_comisiones,
                comission_agent = total_comisiones / 2
            )
            return generate_invoice(request, booking_no)


        def format_time_24_to_12(time_str):
            try:
                if not time_str:
                    return ""

                time_obj = datetime.strptime(time_str, "%H%M")
                return time_obj.strftime("%I:%M %p").lstrip('0').replace(' 0', ' ')
            except ValueError:
                return time_str

        itinerario_reorganizado = []
        for idx, item in enumerate(itinerario):
            if item.departure_port_name == "At Sea":
                time_str = ""
            else:
                prev_item = itinerario[idx - 1] if idx > 0 else None
                current_item = item

                prev_arrival_time = format_time_24_to_12(prev_item.arrival_time) if prev_item else ""
                current_departure_time = format_time_24_to_12(current_item.departure_time)

                if prev_arrival_time and current_departure_time:
                    time_str = f"{prev_arrival_time} — {current_departure_time}"
                elif prev_arrival_time:
                    time_str = f"{prev_arrival_time}"
                elif current_departure_time:
                    time_str = f"{current_departure_time}"
                else:
                    time_str = ""

            itinerario_reorganizado.append({
                'dia': idx + 1,
                'port_name': item.departure_port_name,
                'time': time_str
            })
            request.session['itinerario_reorganizado'] = json.dumps(itinerario_reorganizado, cls=DjangoJSONEncoder)

        if itinerario.exists():
            ultimo_item = itinerario.last()
            if ultimo_item.arrival_port_name == "At Sea":
                time_str = ""
            else:
                time_str = format_time_24_to_12(ultimo_item.arrival_time)

            itinerario_reorganizado.append({
                'dia': len(itinerario) + 1,
                'port_name': ultimo_item.arrival_port_name,
                'time': time_str
            })

        return render(request, 'payment_prod.html', {
            'charge_totals': charge_totals,
            'additional_charges_sum': additional_charges_sum,
            'booking_context': root.iter(),
            'passenger_data_json': passenger_data_json,
            'xml_data': xml_data,
            'response_content': response_content,
            'cruise': cruise_id,
            'cabin_number': cabin_number,
            'itemtype_list': itemtype_list,
            'itemcode_list': itemcode_list,
            'packagecode_list': packagecode_list,
            'category_list': category_list,
            'booking_no': booking_no,
            'total': total,
            'desembarkation_port': desembarkation_port,
            'embarkation_port': embarkation_port,
            'total_general': total_general,
            'crucero': crucero,
            'metodo_pago': metodo_pago,
            'moneda': moneda,
            'fecha_salida': fecha_salida,
            'fecha_regreso': fecha_regreso,
            'categoria': categoria,
            'lock_id': lock_id,
            'total_travelers': total_travelers,
            'price_variable': price_variable,
            'precio': precio,
            'charge_details': charge_details,
            'booking_charges': booking_charges,
            'deposit_amount_due': deposit_amount_due,
            'final_payment_date': final_payment_date_formatted,
            'deposit_due_date': deposit_due_date_formatted,
            'total_payments_received': total_payments_received,
            'debug_info': {
                'cruise_id': cruise_id,
                'price_variable': price_variable,
                'cabin_number': cabin_number,
                'priceType': priceType,
                'fareCode': fareCode,
                'actual_price_from_model': precio,
                'one_pax': one_pax,
                'two_pax': two_pax,
                'three_pax': three_pax,
                'four_pax': four_pax,
                'crucero': crucero,
                'price_per_adult': precio / adults if adults > 0 else 0,
            },
            'crucero_fields': {k: v for k, v in crucero.__dict__.items() if not k.startswith('_')},
            'one_pax': one_pax,
            'two_pax': two_pax,
            'three_pax': three_pax,
            'four_pax': four_pax,
            'cabin_categories': cabin_categories,
            'items_por_categoria': itemcode_list,
            'returnDate': (crucero.sailingDate + timedelta(days=crucero.nights)).strftime('%Y-%m-%d'),
            'charges': charges,
            'current_datetime': current_datetime,
            'passenger_data': passenger_data,
            'additional_charges_sum': additional_charges_sum,
            'download_invoice_url': reverse('generate_invoice'),
            'experiencia': experiencia_list,
            'itinerario_reorganizado': itinerario_reorganizado,
        })

    def format_time_24_to_12(time_str):
            try:
                if not time_str:
                    return ""

                time_obj = datetime.strptime(time_str, "%H%M")
                return time_obj.strftime("%I:%M %p").lstrip('0').replace(' 0', ' ')
            except ValueError:
                return time_str
    itinerario_reorganizado = []

    for idx, item in enumerate(itinerario):
        if item.departure_port_name == "At Sea":
            time_str = ""
        else:
            prev_item = itinerario[idx - 1] if idx > 0 else None
            current_item = item

            prev_arrival_time = format_time_24_to_12(prev_item.arrival_time) if prev_item else ""
            current_departure_time = format_time_24_to_12(current_item.departure_time)

            if prev_arrival_time and current_departure_time:
                time_str = f"{prev_arrival_time} — {current_departure_time}"
            elif prev_arrival_time:
                time_str = f"{prev_arrival_time}"
            elif current_departure_time:
                time_str = f"{current_departure_time}"
            else:
                time_str = ""

        itinerario_reorganizado.append({
            'dia': idx + 1,
            'port_name': item.departure_port_name,
            'time': time_str
        })

    if itinerario.exists():
        ultimo_item = itinerario.last()
        if ultimo_item.arrival_port_name == "At Sea":
            time_str = ""
        else:
            time_str = format_time_24_to_12(ultimo_item.arrival_time)

        itinerario_reorganizado.append({
            'dia': len(itinerario) + 1,
            'port_name': ultimo_item.arrival_port_name,
            'time': time_str
        })


    return render(request, 'bookingpro.html', {
        'itinerario_reorganizado': itinerario_reorganizado,
        'dining_options': dining_options,
        'formset': formset,
        'cruise': cruise_id,
        'debug_info': {
            'cruise_id': cruise_id,
            'price_variable': price_variable,
            'cabin_number': cabin_number,
            'priceType': priceType,
            'fareCode': fareCode,
            'actual_price_from_model': precio,
            'one_pax': one_pax,
            'two_pax': two_pax,
            'three_pax': three_pax,
            'four_pax': four_pax,
            'crucero': crucero,
            'price_per_adult': precio / adults if adults > 0 else 0,
        },
        'price_variable': price_variable,
        'total_travelers': total_travelers,
        'item_list': items_list,
        'precio': precio,
        'crucero_fields': {k: v for k, v in crucero.__dict__.items() if not k.startswith('_')},
        'crucero': crucero,
        'total_general': total_general,
        'itinerario': itinerario,
        'cabin_number': cabin_number,
        'category_list': category_list,
        'cabin_categories': cabin_categories,
        'items_list': itemcode_list,
        'returnDate': (crucero.sailingDate + timedelta(days=crucero.nights)).strftime('%B %d, %Y'),
        'experiencia': experiencia_list,
        'total_three_pax': total_three_pax,
    })



from urllib.parse import quote


def record_payment(request, booking_no):
    booking = get_object_or_404(Booking, booking_number=booking_no)
    identifaction = booking.unique_id
    error_message = request.GET.get('error', None)

    form_data = {
        'payment_amount': request.POST.get('payment_amount', ''),
        'credit_card_code': request.POST.get('credit_card_code', ''),
        'credit_card_number': request.POST.get('credit_card_number', ''),
        'name_on_credit_card': request.POST.get('name_on_credit_card', ''),
        'ccv_code': request.POST.get('ccv_code', ''),
        'expiration_month': request.POST.get('expiration_month', ''),
        'expiration_year': request.POST.get('expiration_year', '')
    }

    if request.method == 'POST':
        payment_amount_str = request.POST.get('payment_amount', '0.00')

        try:

            payment_amount = Decimal(payment_amount_str)
            if payment_amount <= 0:
                raise ValueError("El monto debe ser mayor a 0.")
        except (ValueError, InvalidOperation):
            return render(request, 'record_payment.html', {
                'booking': booking,
                'form_data': form_data,
                'error': 'Monto no válido'
            })

        credit_card_code = request.POST.get('credit_card_code')
        credit_card_number = request.POST.get('credit_card_number')
        name_on_credit_card = request.POST.get('name_on_credit_card')
        ccv_code = request.POST.get('ccv_code')
        expiration_month = request.POST.get('expiration_month')
        expiration_year = request.POST.get('expiration_year')

        address = request.POST.get('address')
        zipcode = request.POST.get('zipcode')
        state = request.POST.get('state')
        typecard = request.POST.get('credit_card_code')
        city = request.POST.get('city')
        country = request.POST.get('country')

        if credit_card_number:
            last_four_digit_card = credit_card_number[-4:]

        if not (credit_card_number and credit_card_code and name_on_credit_card and ccv_code and expiration_month and expiration_year):
            return render(request, 'record_payment.html', {
                'booking': booking,
                'error': 'Please complete all the credit card fields.',
                'form_data': form_data,
            })

        if not request.user.is_authenticated:
            return redirect('login')

        print(f"Procesando pago de {payment_amount} para la reserva {booking_no}...")

        url = 'https://wsrv.msccruises.com/upp/proxy/push/b5383d345a695897'

        headers = {
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': '0cf43a5e90d824440ea9b809b153dcfb4d5960ecb450442c904c1d28b16d8aa0',
            'AgentID': 'US159929',
        }

        xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
            <DtsApplyPaymentRequestMessage xmlns="DTS">
                <BookingContext>
                    <AgencyID>US159929</AgencyID>
                    <BookingContactName>ThatVacation</BookingContactName>
                    <BookingNo>{booking_no}</BookingNo>
                    <BookingChannel>XML</BookingChannel>
                </BookingContext>
                <Payment>
                    <ReceivedFrom>fusco</ReceivedFrom>
                    <PaymentAmount>{payment_amount}</PaymentAmount>
                    <FormOfPaymentCode>CC</FormOfPaymentCode>
                    <CreditCardInfo>
                        <CreditCardCode>{credit_card_code}</CreditCardCode>
                        <CreditCardNumber>{credit_card_number}</CreditCardNumber>
                        <NameOnCreditCard>{name_on_credit_card}</NameOnCreditCard>
                        <CCVCode>{ccv_code}</CCVCode>
                        <Process>true</Process>
                        <ExpirationDate>
                            <ExpirationMonth>{expiration_month}</ExpirationMonth>
                            <ExpirationYear>{expiration_year}</ExpirationYear>
                        </ExpirationDate>
                    </CreditCardInfo>
                </Payment>
            </DtsApplyPaymentRequestMessage>
        '''

        response = requests.post(url, headers=headers, data=xml_data.encode('utf-8'))
        response_content = response.content.decode('utf-8', 'ignore')

        print("Contenido completo de la respuesta XML:")
        print(response_content)

        if response.status_code == 200:
            try:

                namespaces = {'dts': 'DTS'}
                root = ET.fromstring(response_content)
                advisory_message = root.find('.//dts:AdvisoryMessage', namespaces)

                if advisory_message is not None:
                    message_type = advisory_message.find('dts:MessageType', namespaces).text.strip()
                    message_text = advisory_message.find('dts:MessageText', namespaces).text.strip()

                    if message_type == 'F':
                        print(f"Error en el pago: {message_text}")
                        encoded_message = quote(message_text)
                        return redirect(f'{request.path}?error={encoded_message}')
                    print(f"Pago procesado con éxito para la reserva {booking_no}")

            except ET.ParseError as e:
                print(f"Error al analizar el XML: {str(e)}")

                return render(request, 'record_payment.html', {
                    'booking': booking,
                    'error': "Error al procesar la respuesta del pago. Por favor, inténtelo de nuevo.",
                    'form_data': form_data,
                })

            print(f"Pago procesado con éxito para la reserva {booking_no}")
            success_message = f"Pay for {payment_amount} succesfull."
            booking.total_paid += payment_amount
            booking.balance = booking.total_to_pay - booking.total_paid
            booking.last_payment_date = timezone.now()
            booking.card_address = address
            booking.last_four_digit_card = last_four_digit_card
            booking.zip_code = zipcode
            booking.type_card = typecard
            booking.city = city
            booking.state = state
            booking.country = country
            booking.save()

            booking_number = booking_no
            return generate_invoice_postpay(request, booking_number)
            return render(request, 'payment_success.html', {
                'booking': booking,
                'success': success_message,
                'identifaction':identifaction,
                'payment_amount':payment_amount,
                'booking_balance':booking.balance,
            })


        else:
            print(f"Error al procesar el pago: {response.status_code}")
            print(f"Detalles del error: {response_content}")
            return render(request, 'record_payment.html', {
                'booking': booking,
                'error': f"Error al procesar el pago: {response_content}"
            })


    return render(request, 'record_payment.html', {'booking': booking, 'booking_no': booking_no})



from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, PageTemplate, Frame
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from datetime import datetime
from decimal import Decimal
import io
import os
import xml.etree.ElementTree as ET
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import Color, black, whitesmoke
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from django.core.mail import EmailMessage


def format_cabin_image_path(ship_name, cabin_type):
    if isinstance(cabin_type, dict):
        cabin_type_name = list(cabin_type.keys())[0]
    else:
        cabin_type_name = cabin_type

    cabin_type_map = {
        'inside': 'INTERIOR',
        'balcon': 'BALCONY'
    }

    cabin_type_name_lower = cabin_type_name.lower()
    if cabin_type_name_lower in cabin_type_map:
        formatted_cabin_type = cabin_type_map[cabin_type_name_lower]
    else:
        formatted_cabin_type = cabin_type_name.strip().replace(' ', '').upper()


    formatted_name = ship_name.strip().upper()
    image_path = os.path.join(settings.STATIC_ROOT, 'images', 'msc_cabinas', f'{formatted_name} {formatted_cabin_type}.jpg')

    if os.path.exists(image_path):
        return image_path
    else:
        return f"Imagen no encontrada. Ruta intentada: {image_path}"



def logo_ship(ship_name):

    ship_name = ship_name.upper()
    if ship_name.startswith("MSC"):
        return os.path.join(settings.STATIC_ROOT, 'msc', 'msc1.png')
    # elif ship_name.startswith("CARNIVAL"):
    #     return os.path.join('static', 'carnival', 'logo.png')
    # elif ship_name.startswith("ROYAL"):
    #     return os.path.join('static', 'royal', 'logo.png')

    return os.path.join('static', 'default', 'logo.png')



def format_ship_image_path(ship_name):
    formatted_name = ship_name.strip().upper()

    image_path = os.path.join(settings.STATIC_ROOT, 'images', 'ships', f'{formatted_name}.jpg')

    if os.path.exists(image_path):
        return image_path
    else:
        return f"Imagen no encontrada. Ruta intentada: {image_path}"


def parse_xml_response(xml_content):
    namespaces = {'dts': 'DTS'}
    root = ET.fromstring(xml_content)

    def decimal_to_string(value):
        try:

            return str(Decimal(value).quantize(Decimal('0.01')))
        except (TypeError, ValueError):
            return value

    booking_info = {
        'booking_no': root.find('.//dts:BookingNo', namespaces).text,
        'booking_charges': decimal_to_string(root.find('.//dts:BookingCharges/dts:BookingCharges', namespaces).text),
        'deposit_amount_due': decimal_to_string(root.find('.//dts:DepositAmountDue', namespaces).text),
        'deposit_due_date': root.find('.//dts:DepositDueDate', namespaces).text,
        'final_payment_date': root.find('.//dts:FinalPaymentDate', namespaces).text,
        'total_net_price': decimal_to_string(root.find('.//dts:TotalNetPrice', namespaces).text),
        'total_payments_received': decimal_to_string(root.find('.//dts:TotalPaymentsReceived', namespaces).text),
        'currency_code': root.find('.//dts:BookingCurrencyCode', namespaces).text,
        'pay_method': root.find('.//dts:PayMethod', namespaces).text,
        'cabin_no': root.find('.//dts:CabinNo', namespaces).text,
    }

    charge_details = {}
    for charge in root.findall('.//dts:ChargesForComponent', namespaces):
        person_no = charge.find('dts:PersonNo', namespaces).text
        charge_type = charge.find('dts:ChargeTypeCode', namespaces).text
        charge_desc = charge.find('dts:ChargeDesc', namespaces).text
        gross_charge_amount = decimal_to_string(charge.find('dts:GrossChargeAmount', namespaces).text)

        if person_no not in charge_details:
            charge_details[person_no] = {
                'details': [],
                'total': Decimal('0.00'),
                'rowspan': 0
            }

        charge_details[person_no]['details'].append({
            'type': charge_type,
            'desc': charge_desc,
            'amount': gross_charge_amount
        })

        charge_details[person_no]['total'] += Decimal(gross_charge_amount)
        charge_details[person_no]['rowspan'] += 1

    for person_no, details in charge_details.items():
        details['total'] = decimal_to_string(details['total'])

    return booking_info, charge_details



light_aqua_blue = Color(0.05, 0.4, 0.6)

def footer(canvas, doc):
    page_width = doc.pagesize[0]
    page_height = doc.pagesize[1]

    font_size = 8
    canvas.setFont('Helvetica', font_size)


    canvas.setFillColor(light_aqua_blue)

    rect_height = 35
    rect_y_position = 0
    canvas.rect(0, rect_y_position, page_width, rect_height, stroke=0, fill=1)

    canvas.setFillColor(black)

    logo_x_position = 10
    logo_width = 1.2 * inch
    logo_height = 0.45 * inch
    logo_margin_right = 100

    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo3.png')

    if os.path.exists(logo_path):
        logo_y_position = rect_y_position + (rect_height - logo_height) / 2
        canvas.drawImage(logo_path, logo_x_position, logo_y_position, width=logo_width, height=logo_height, mask='auto')
    else:
        logo_y_position = rect_y_position

    canvas.setFillColor(colors.white)

    terms_text = "Terms & Conditions"
    terms_link = "https://thatvacationtravel.com/termcondition/"
    terms_x_position = logo_x_position + logo_width + 10
    terms_y_position = logo_y_position + logo_height / 2 - font_size / 2
    canvas.drawString(terms_x_position, terms_y_position, terms_text)
    terms_text_width = canvas.stringWidth(terms_text, 'Helvetica', font_size)
    canvas.linkURL(terms_link, (terms_x_position, terms_y_position, terms_x_position + terms_text_width, terms_y_position + font_size), thickness=1, color=colors.blue)

    footer_texts = [
        "+1 305-428-2518",
        "booking@thatvacation.com",
        "12150 Sw 128 Court Suite 102, Miami, FL, 33186 USA"
    ]

    text_start_x_position = logo_x_position + logo_width + logo_margin_right
    spacing = 20

    x_position = text_start_x_position
    y_position = rect_y_position + rect_height / 2 - font_size / 2

    for text in footer_texts:
        canvas.drawString(x_position, y_position, text)
        x_position += canvas.stringWidth(text, 'Helvetica', font_size) + spacing

def format_time_24_to_12(time_str):
    try:
        if not time_str:
            return ""
        time_obj = datetime.strptime(time_str, "%H%M")
        return time_obj.strftime("%I:%M %p").lstrip('0').replace(' 0', ' ')
    except ValueError:
        return time_str



def generate_invoice(request, booking_no):
    border_color = HexColor("#257fb2")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', alignment=1))
    styles.add(ParagraphStyle(name='RightHeading', alignment=2))
    light_gray = Color(200 / 255, 200 / 255, 200 / 255)
    light_gray2 = Color(200 / 255, 200 / 255, 200 / 255)
    light_aqua_blue = Color(0.05, 0.4, 0.6)
    lighter_aqua_blue1 = Color(0.1, 0.5, 0.7)
    data_booking = get_object_or_404(Booking, booking_number=booking_no)
    data_invoice = get_object_or_404(InvoiceCustomer, booking_no=booking_no)
    unique_id = data_booking.unique_id

    dining_mapping_msc = {
        'CL': 'LATE / 7:45PM-9:45PM',
        'CE': 'EARLY / 5:30PM-7:30PM',
        'M': 'FIRST SITTING / 6:00PM',
        'L': 'SECOND SITTING / 8:00PM ',
    }

    dining_description = dining_mapping_msc.get(data_booking.dining, 'Unknown')

    create_date = data_booking.created_at
    last_payment_date = data_booking.last_payment_date
    fecha_regreso = data_invoice.fecha_regreso
    xml_content = data_invoice.debug_info
    passenger_data = data_invoice.passenger_data
    crucero = data_invoice.crucero
    cruceroId = data_invoice.cruise
    total_travelers = data_invoice.total_travelers
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cabin_type = data_invoice.category_list
    booking_charges = data_invoice.total_general
    deposit_amount_due = data_invoice.deposit_amount_due
    payments_received = data_booking.total_paid
    cabin_number = data_invoice.cabin_number
    departure_date = data_invoice.fecha_salida
    balance = data_booking.balance
    desposit_due_date = data_invoice.desglose_passenger_data
    passenger_data_str = data_invoice.passenger_data
    booking_context = data_invoice.booking_context
    itin_cd = get_itin_cd(booking_context)

    fecha_regreso_str = data_invoice.fecha_regreso
    departure_date_str = data_invoice.fecha_salida

    formatted_date3 = create_date.strftime('%Y-%m-%d %H:%M')
    fromatted_date4 = last_payment_date.strftime('%Y-%m-%d %H:%M')

    fecha_regreso1 = datetime.strptime(fecha_regreso_str, "%Y-%m-%d").date()
    departure_date1 = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
    night = (fecha_regreso1 - departure_date1).days

    itineraries = Itinerary.objects.filter(
        Q(cruise_id=cruceroId) &
        Q(itinerary_cd=itin_cd)
    )

    desglose_passenger_data = data_invoice.desglose_passenger_data

    try:
        json_data = json.loads(desglose_passenger_data)

        deposit_due_date_str = json_data['booking_info']['deposit_due_date']
        deposit_due_date = parse_date(deposit_due_date_str)
        formatted_date = format_date1(deposit_due_date)

        final_payment_date_str = json_data['booking_info']['final_payment_date']
        final_payment_date = parse_date(final_payment_date_str)
        formatted_final_payment_date = format_date1(final_payment_date)

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        print("Error parsing date information:", e)
        formatted_date = ""
        formatted_final_payment_date = ""


    try:
        cabin_categories = json.loads(data_invoice.cabin_categories)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        cabin_categories = {}

    if isinstance(cabin_categories, dict) and len(cabin_categories) > 0:
        cabin_type_name = list(cabin_categories.keys())[0]
    else:
        cabin_type_name = None


    try:
        cabin_categories = json.loads(data_invoice.cabin_categories)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        cabin_categories = {}

    if isinstance(cabin_categories, dict) and len(cabin_categories) > 0:
        cabin_type_name = list(cabin_categories.keys())[0]
    else:
        cabin_type_name = None

    fecha_actual = datetime.now().strftime("%Y%m%d")

    if not xml_content or not passenger_data:
        return render(request, 'error.html', {'mensaje_error': 'Datos de sesión incompletos.'})

    booking_info, charge_details = parse_json_response(xml_content)


    fecha_actual = datetime.now().strftime("%Y%m%d")


    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"TVT_{fecha_actual}_{booking_no}.pdf")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=20, leftMargin=10, rightMargin=10, bottomMargin=20)


    def add_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(8.0 * inch, 10.8 * inch, f"TVT-{unique_id}")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='header', frames=[frame], onPage=add_header)
    doc.addPageTemplates([template])


    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', alignment=1))
    styles.add(ParagraphStyle(name='RightHeading', alignment=2))

    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo_oficial1.png')

    warning_text = "WARNING: This document is not a ticket nor an invoice. It is issued once the booking is confirmed and following each change."
    warning_style = ParagraphStyle(
        'WarningStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        alignment=1,
        textColor=colors.black,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    warning_paragraph = Paragraph(warning_text, warning_style)

    card_data = [[warning_paragraph]]

    card_table = Table(
        card_data,
        colWidths=[0.95 * inch * 8.5],
        rowHeights=[None],
        style=[
            ('BACKGROUND', (0, 0), (-1, -1), None),
            ('BOX', (0, 0), (-1, -1), 0.5, black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]
    )

    elements.append(card_table)
    elements.append(Spacer(1, 0.6 * inch))


    if os.path.exists(logo_path):
        logo = Image(logo_path, 1.7 * inch, 0.9 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    else:
        error_message = Paragraph(f"<b>Logo no encontrado en la ruta:</b> {logo_path}")
        elements.append(error_message)

    elements.append(Spacer(1, 0.2 * inch))

    invoice_info_style = ParagraphStyle(
        'InvoiceInfoStyle',
        parent=styles['Normal'],
        fontSize=28,
        leading=20,
        alignment=1,
        fontName='Helvetica',
        spaceBefore=20,
        textColor=black,
    )

    invoice_info_style1 = ParagraphStyle(
        'InvoiceInfoStyle1',
        parent=styles['Normal'],
        fontSize=16,
        leading=20,
        alignment=1,
        fontName='Helvetica',
        spaceBefore=20,
        textColor=black,
    )

    justified_style = ParagraphStyle(
        name="Justified",
        parent=getSampleStyleSheet()['Normal'],
        alignment=TA_JUSTIFY,
        leading=12,
        spaceAfter=10,
        fontSize=10,
    )

    ship_name = crucero
    image_ship_path = format_ship_image_path(ship_name)
    cabin_image_path = format_cabin_image_path(ship_name, cabin_type_name)
    logo_path = logo_ship(ship_name)

    ship_image = Image(image_ship_path, 1.5 * inch, 1 * inch) if os.path.exists(image_ship_path) else "Imagen no disponible"
    cabin_image = Image(cabin_image_path, 1.5 * inch, 1 * inch) if os.path.exists(cabin_image_path) else cabin_type

    items_list = request.session.get('items_list', [])

    experiencia_list = request.session.get('experiencia_list', [])
    experiencia_display = '.<br/>'.join([desc_long for _, desc_long in experiencia_list if desc_long]) if experiencia_list else 'No experience descriptions'
    experiencia_paragraph = Paragraph(experiencia_display, justified_style)

    items_display = request.session.get('name_experience', [])
    items_display_joined = ', '.join(items_display)

    items_display_paragraph = Paragraph(items_display_joined, justified_style)

    if os.path.exists(logo_path):
        logo_image = Image(logo_path, 1.0 * inch, 0.7 * inch)
    else:
        logo_image = ship_name

    payment_receive = request.session.get('payment_amount', 0)
    booking_charges = data_invoice.total
    balance_due =  float(booking_charges) - float(payment_receive)
    url_policy = "https://thatvacation.com/static/terms_conditions/msc_terminos.pdf"


    styles = getSampleStyleSheet()
    hyperlink_style = styles['Normal']
    hyperlink_style.fontName = 'Helvetica'
    hyperlink_style.textColor = colors.blue
    hyperlink_style.fontSize = 10

    link_text = f'<a href="{url_policy}">Click here</a>'
    link_paragraph = Paragraph(link_text, hyperlink_style)

    booking_details_data = [
        [""],
        [f"Booking #: {booking_no}", f"Created: {formatted_date3}", logo_image],
        ["Quantity Travel:", total_travelers, ""],
        ["Booking Charges:", booking_charges, ""],
        ["Deposit Amount Due:", deposit_amount_due, ""],
        ["Payments Received:", payments_received, ""],
        ["Balance:", balance, ""],
        ["Last Payment Date", fromatted_date4, ""],
        ["Deposit Due Date:", deposit_due_date_str, ""],
        ["Final Payment Date:", final_payment_date_str, ""],
        ["Cancellation policy ", link_paragraph],
        [""],
        ["Experience:", items_display_paragraph, ""],
        [""],
        ["Package Included:", experiencia_paragraph, ""],
        [""],
        [""],
        [""],
        ["Ship Name:", ship_name, ship_image, ""],
        [""],
        ["Cabin Type:", cabin_type_name, cabin_image],
        ["Cabin Number:", cabin_number, ""],
        ["Night:", night, ""],
        ["Departure Date:", departure_date, ""],
        ["Return Date:", fecha_regreso, ""],
        ["Dining:", dining_description, ""],
    ]

    booking_details = Table(booking_details_data, colWidths=[1.5 * inch, 4.8 * inch, 1 * inch])
    booking_details.setStyle(TableStyle([
        ('SPAN', (0, 0), (2, 0)),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGNMENT', (0, 0), (-1, 0), 'LEFT'),

        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (2, 10), (2, 11), 'CENTER'),
        ('VALIGN', (2, 10), (2, 11), 'MIDDLE'),
    ]))
    elements.append(booking_details)
    elements.append(Spacer(1, 0.20 * inch))

    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Heading3'],
        fontSize=14,
        alignment=1,
        spaceAfter=20,
        textColor=light_aqua_blue,
        fontName='Helvetica-Bold'
    )

    itinerario_reorganizado = []
    for idx, itinerary in enumerate(itineraries):
        port_name = itinerary.departure_port_name or itinerary.arrival_port_name
        departure_time = itinerary.departure_time or "N/A"
        arrival_time = itinerary.arrival_time or "N/A"

        departure_time_clean = format_time_invoice(departure_time) if departure_time != "N/A" else ""
        arrival_time_clean = format_time_invoice(arrival_time) if arrival_time != "N/A" else ""

        if port_name == "At sea":
            formatted_line = f"Day {idx + 1}: At sea"
        else:
            if idx == 0:
                if departure_time_clean:
                    formatted_line = f"Day {idx + 1}: {port_name} Departure: {departure_time_clean}"
                else:
                    formatted_line = f"Day {idx + 1}: {port_name}"
            else:
                time_info = []
                if arrival_time_clean:
                    time_info.append(f"Arrival: {arrival_time_clean}")
                if departure_time_clean:
                    time_info.append(f"Departure: {departure_time_clean}")
                time_info_str = " - ".join(time_info) if time_info else "No times available"
                formatted_line = f"Day {idx + 1}: {port_name} {time_info_str}"

        itinerario_reorganizado.append({
            'dia': idx + 1,
            'port_name': port_name.strip(),
            'departure_time': departure_time_clean.strip(),
            'arrival_time': arrival_time_clean.strip(),
            'arrival_port_name': itinerary.arrival_port_name,
            'arrival_day': itinerary.arrival_day,
            'formatted_line': formatted_line
        })

    if itinerario_reorganizado:
        last_objects_itinerary = itinerario_reorganizado[-1]
    else:
        last_objects_itinerary = None

    itinerario_lines = [item['formatted_line'] for item in itinerario_reorganizado]

    last_itinerary_text = ""
    if last_objects_itinerary:
        last_itinerary_text = (
            f"<br />"
            f"Day {last_objects_itinerary['arrival_day']}: {last_objects_itinerary['arrival_port_name']} Arrival: {last_objects_itinerary['arrival_time']}"
        )

    itinerario_text = "<br />".join(itinerario_lines)
    if last_itinerary_text:
        itinerario_text += f"{last_itinerary_text}"

    itinerario_paragraph = Paragraph(itinerario_text, justified_style)

    elements.append(Paragraph("Ship Itinerary", header_style))
    elements.append(Spacer(1, 0.20 * inch))
    elements.append(itinerario_paragraph)
    elements.append(Spacer(1, 0.20 * inch))

    elements.append(PageBreak())

    charge_totals_json = data_invoice.desglose_passenger_data
    charge_totals = json.loads(charge_totals_json)

    charge_details_table_data = [['Passenger', 'Charge Type', 'Description', 'Amount']]
    grand_total = 0.00
    total_passenger_indices = []

    for person_no, data in charge_totals.get('charge_details', {}).items():
        total_srn = 0.0
        total_cab = 0.0
        total_chd = 0.0
        total_pch = 0.0

        for detail in data['details']:
            charge_type = detail['type']
            amount = float(detail['amount'])
            if charge_type == 'SRN':
                total_srn += amount
            elif charge_type == 'CAB':
                total_cab += amount
            elif charge_type == 'CHD':
                total_chd += amount
            elif charge_type == 'PCH':
                total_pch += amount

        total_passenger = total_cab + total_chd + total_srn + total_pch

        if total_cab > 0:
            charge_details_table_data.append([
                person_no,
                'CAB',
                'Cabin Charges',
                f"${total_cab + total_srn:.2f}"
            ])

        if total_chd > 0:
            charge_details_table_data.append([
                person_no,
                'CHD',
                'Child Cabin Charges',
                f"${total_chd + total_srn:.2f}"
            ])

        if total_pch > 0:
            charge_details_table_data.append([
                person_no,
                'PCH',
                'Port Charge & Tax',
                f"${total_pch:.2f}"
            ])

        charge_details_table_data.append([
            person_no,
            'Total Passenger',
            '-',
            f"${total_passenger:.2f}"
        ])
        total_passenger_indices.append(len(charge_details_table_data) - 1)
        grand_total += total_passenger

    charge_details_table_data.append([
        '',
        'Total to pay',
        '',
        f"${grand_total:.2f}"
    ])

    charges_table = Table(charge_details_table_data, colWidths=[1 * inch, 2 * inch, 3 * inch, 2 * inch])
    charges_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.black),
        ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    for index in total_passenger_indices:
        charges_table.setStyle(TableStyle([
            ('BACKGROUND', (0, index), (-1, index), colors.lightgrey),
            ('TEXTCOLOR', (0, index), (-1, index), colors.black),
            ('FONTNAME', (0, index), (-1, index), 'Helvetica-Bold'),
        ]))

    elements.append(charges_table)
    elements.append(Spacer(1, 0 * inch))


    try:
        passenger_data = json.loads(passenger_data_str)

        invoice_info_style1 = ParagraphStyle(
            'InvoiceInfoStyle1',
            parent=styles['Normal'],
            fontSize=12,
            leading=20,
            alignment=1,
            fontName='Helvetica',
            spaceBefore=20,
            textColor=black,
        )

        for i, passenger in enumerate(passenger_data):
            if i == 0:
                invoice_info_paragraph = Paragraph(f"<p>Passenger # {i + 1}</p>", invoice_info_style1)
                booking_details_data_travel = [
                    [invoice_info_paragraph],
                    ["Full Name", f"{passenger['first_name']} {passenger['last_name']}"],
                    ["Email & Phone Number", f"{passenger['email']}", f"+{passenger['telephone_no']}"],
                    ["Date of Birth", f"{passenger['date_of_birth']}", "-"],
                    ["Gender & Title", f"{passenger['gender']}", "Male" if passenger['gender'] == 'M' else "Female" if passenger['gender'] == 'F' else "-"],
                    ["City & State", f"{passenger['city']}, {passenger['state_province']}", "-"],
                ]
            else:
                invoice_info_paragraph = Paragraph(f"<p>Passenger # {i + 1}</p>", invoice_info_style1)
                booking_details_data_travel = [
                    [invoice_info_paragraph],
                    ["Full Name", f"{passenger['first_name']} {passenger['last_name']}"],
                    ["Date of Birth", f"{passenger['date_of_birth']}", "-"],
                    ["Gender & Title", f"{passenger['gender']}", "Male" if passenger['gender'] == 'M' else "Female" if passenger['gender'] == 'F' else "-"],
                ]

            booking_details = Table(booking_details_data_travel, colWidths=[2 * inch, 4 * inch, 2 * inch])
            booking_details.setStyle(TableStyle([
                ('SPAN', (0, 0), (2, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), lighter_aqua_blue1),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGNMENT', (0, 0), (-1, 0), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('GRID', (0, 1), (-1, -1), 0.25, colors.black),
            ]))
            elements.append(booking_details)
            elements.append(Spacer(1, 0 * inch))

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")

    elements.append(PageBreak())

    documentation_style = ParagraphStyle('DocumentationStyle', parent=styles['Normal'], fontSize=10, leading=12, spaceBefore=10, spaceAfter=10, textColor=colors.black, alignment=TA_JUSTIFY, leftIndent=3, rightIndent=3)
    text_booking_details = Paragraph("""
        <p>
        <b>Online Check-In: Download APP. "Cruise line"</b><br/>
        Guests are requested to complete their Online Check-In form at least 21 days and up to 3 days prior to your vacation start date. Guests who have not completed their online Check-In forms at 3 days prior to their vacation start date are required to complete the Check-In process at the pier at least 2 hours prior to the departure time noted on their cruise documents.<br />
        <br />
        <b>Warning:</b> <br />
        The balance due must be paid in full by the final payment date listed above to prevent your booking from cancelling.
        <br />
        <br />
        <b>Important:</b> <br />
        *A change fee of $100 USD per guest will apply for ship or sail date changes.<br />
        *Within 24 hours you will receive your booking confirmation
        </p>
        <br/>
        <br />
        <b>Documentation and Immigration Requirements.</b><br/>
        Guests are highly encouraged to travel with a valid passport, even when not required. <br/>
        <br/>
        For your protection, we recommend that your passport expiration date does not occur within six (6) months of the sailing return date.<br/>
        <br/>
        Some foreign ports of call require a visa. Please contact the Embassy (Consular Services) of each country on your sailing itinerary or the visa service of your choice for specific
        visa requirements, information, forms and fees for your nationality. That Vacation Travel Corp. suggests the visa provider, CIBT at <link href="https://www.visacentral.com" color="blue">www.visacentral.com</link>.<br/>
        <br/>
        The spelling of the guest(s) name as booked for a cruise must match exactly as their valid passport or proof of citizenship / identification during ship check-in formalities. <br/>
        <br/>
        Certain countries may have specific travel requirements for your itinerary.<br/>
        <br/>
        All guests (including children) must present a valid passport when sailing on U.S. Open Loop voyages. These are voyages that commence in a U.S. port, travel within the
        Western Hemisphere, and end at a different U.S. port. When traveling on these sailings, please take extra caution in understanding the specific documentation
        requirements.<br/>
        <br/>
        All guests (including children) require specific travel documents that may include either a passport or other documentation, such as a government-issued birth certificate and
        laminated government issued picture ID denoting photo, name and date of birth, when traveling on U.S. Closed Loop voyages. These are voyages that commence
        and end in the same U.S. port without leaving the western hemisphere. Please note that Baptismal papers, hospital certificates of birth, voter registration cards or
        Social Security cards are not considered proof of citizenship.<br/>
        <br/>
        Should the last names of the parent and minor child traveling with them differ, the parent is required to present the child's valid passport and visa (if required) and the child's
        birth certificate (original, a notarized copy or a certified copy). The name of the parent(s) and the child must be linked through legal documentation.<br/>
        <br/>
        Adults who are not the parent or legal guardian of a minor traveling with them must present an original notarized letter signed by the child's parent(s), authorizing the adult to
        take the child on the specific cruise, supervise the child and allow emergency medical treatment to be administered.<br/>
        <br/>
        Guests on consecutive sailings must ensure they have the proper travel documents for their entire cruise vacation and for any port within their itinerary(s).
        <br/>
        <b>• Age Restrictions:</b><br/>
        This cruise line requires that passengers younger than 21 years old be accompanied by an adult 21 years or older in the same cabin.
        Infants must be at least 3 months old as of the first day of the cruise, with doctor’s approval letter that they can sail. In the event Passenger intends to bring onboard any child under the age of 12 months, the Company recommends seeking medical advice from the child’s physician confirming such child’s fitness to travel on an international ocean voyage.
        <br/>
        <b>• Pregnancy Restrictions:</b><br/>
        Pregnant women are highly recommended to seek medical advice prior to travel at any stage of their pregnancy. The Carrier cannot for safety reasons carry pregnant Passengers of 24 weeks or more by the end of the cruise. The Carrier reserves the right to request a medical certificate at any stage of pregnancy and to refuse passage if the Carrier and/or the Master are not satisfied that the Passenger will be safe during the passage.
        <br/>
        <br/>
        <b>Terms & Condition - Privacy Policy</b><br />

    """, documentation_style)
    elements.append(text_booking_details)
    elements.append(Spacer(1, 0.25 * inch))


    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TVT{fecha_actual}{booking_no}.pdf"'

    request.session['pdf_path'] = pdf_path
    request.session['booking_info'] = booking_info
    request.session['fecha_actual'] = fecha_actual
    request.session['crucero'] = crucero
    request.session['total_travelers'] = total_travelers
    request.session['balance_due'] = balance_due
    request.session['payment_receive'] = payment_receive
    request.session['passenger_data'] = passenger_data
    request.session['items_list'] = items_list
    request.session['experiencia_list'] = experiencia_list
    request.session['grand_total'] = grand_total

    user_email = request.user.email
    passenger_email = passenger_data[0]['email']

    subject = f"Your Cruise Booking Invoice"
    message = """
    <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: auto;
                }
                h2 {
                    color: #007BFF;
                    text-align: center;
                }
                p {
                    line-height: 1.6;
                }
                ul {
                    list-style-type: disc;
                    margin-left: 20px;
                }
                .footer {
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                    font-size: 12px;
                    text-align: center;
                    color: #777;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Your Cruise Booking Invoice</h2>
                <p style="font-weight: bold;">Dear Travel Partner/Guest:</p>
                <p>Please find attached your booking invoice.</p>
                <p>For up-to-date information on our travel protocols and requirements, please visit <a href="https://thatvacation.com/static/terms_conditions/msc_terminos.pdf">this link</a> and <a href="https://thatvacationtravel.com/static/pdf/That%20Vacation%20Travel%20-terms-and-conditions-%20ST38963.pdf">this link</a>.</p>
                <p>Thank you for booking with “That Vacation Travel.” We appreciate your support.</p>
                <p>Attached is a detailed confirmation, including all cruise fares, payment requirements, and cancellation policy.</p>
                <ul>
                    <li>Please review the information to verify that it is correct and contact us at 305-428-2518 if you have any questions or concerns.</li>
                    <li>Once the reservation is in escrow, you or your clients can complete registration or check-in. Download the APP for the product the client purchased (Cruise or Hotel) to save time and receive specific information. This will help them prepare for the best vacation of their life. Sincerely, “That Vacation Travel”</li>
                </ul>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>That Vacation Travel (305) 428-2518</p>
                <div class="footer">
                    <p>Best regards,</p>
                    <p>©2024 That Vacation Travel, All Right Reserved. Designed By That Vacation, ST 38963.<br> Registry: United States of America. 12150 SW 128TH CT STE 102 | Miami, Florida 33186 | 1-305-428-2518 | <a href="https://thatvacation.com/">thatvacation.com</a></p>
                    <p>PLEASE DO NOT REPLY TO THIS MESSAGE. All replies are automatically deleted.</p>
                </div>
            </div>
        </body>
    </html>
    """

    try:
        email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], bcc=['thatvacationtravel@gmail.com'])
        email.content_subtype = 'html'
        email.attach_file(pdf_path)
        email.send()
    except Exception as e:
        return HttpResponse(f"Error sending email: {str(e)}", status=500)

    return success_postpay(request, booking_no)



def success(request):
    pdf_path = request.session.get('pdf_path')
    booking_info = request.session.get('booking_info')
    fecha_actual = request.session.get('fecha_actual')
    crucero = request.session.get('crucero')
    total_travelers = request.session.get('total_travelers')
    balance_due = request.session.get('balance_due')
    payment_receive = request.session.get('payment_receive')
    passenger_data = request.session.get('passenger_data')
    items_list = request.session.get('items_list')
    experiencia_list = request.session.get('experiencia_list')
    grand_total = request.session.get('grand_total')

    context = {
        'pdf_path': pdf_path,
        'booking_info': booking_info,
        'fecha_actual': fecha_actual,
        'crucero': crucero,
        'total_travelers': total_travelers,
        'balance_due': balance_due,
        'payment_receive': payment_receive,
        'passenger_data': passenger_data,
        'items_list': items_list,
        'experiencia_list': experiencia_list,
        'grand_total': grand_total,
    }

    return render(request, 'success.html', context)




def parse_json_response(json_content):
    try:
        if not json_content.strip():
            raise ValueError("El contenido JSON está vacío")

        response_data = json.loads(json_content)

        booking_info = response_data.get('booking_info', {})
        charge_details = response_data.get('charge_details', {})
        return booking_info, charge_details
    except json.JSONDecodeError as e:
        logging.error("Error al decodificar JSON: %s", e)
        raise
    except ValueError as e:
        logging.error("Error en el contenido JSON: %s", e)
        raise


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %Z %Y").date()
    except ValueError as e:
        print(f"Error al convertir la fecha: {date_str} ({e})")
        return None

def format_date1(date_obj):
    if date_obj:
        return date_obj.strftime("%d-%m-%Y")
    return "No disponible"



def get_itin_cd(booking_context):
    try:
        context_dict = json.loads(booking_context)
    except json.JSONDecodeError:
        print("Error: El contenido de booking_context no es un JSON válido.")
        return None

    itin_cd = context_dict.get('itinCd', None)

    return itin_cd



def format_time_invoice(time_str):
    if time_str and len(time_str) == 4:
        return f"{time_str[:2]}:{time_str[2:]}"
    return time_str

from reportlab.lib import colors
from dateutil import parser

def generate_invoice_postpay(request, booking_no):
    border_color = HexColor("#257fb2")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', alignment=1))
    styles.add(ParagraphStyle(name='RightHeading', alignment=2))
    light_gray = Color(200 / 255, 200 / 255, 200 / 255)
    light_gray2 = Color(200 / 255, 200 / 255, 200 / 255)
    light_aqua_blue = Color(0.05, 0.4, 0.6)
    lighter_aqua_blue1 = Color(0.1, 0.5, 0.7)
    data_booking = get_object_or_404(Booking, booking_number=booking_no)
    data_invoice = get_object_or_404(InvoiceCustomer, booking_no=booking_no)
    unique_id = data_booking.unique_id

    create_date = data_booking.created_at
    last_payment_date = data_booking.last_payment_date
    fecha_regreso = data_invoice.fecha_regreso
    xml_content = data_invoice.debug_info
    passenger_data = data_invoice.passenger_data
    crucero = data_invoice.crucero
    cruceroId = data_invoice.cruise
    total_travelers = data_invoice.total_travelers
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cabin_type = data_invoice.category_list
    booking_charges = data_invoice.total_general
    deposit_amount_due = data_invoice.deposit_amount_due
    payments_received = data_booking.total_paid
    cabin_number = data_invoice.cabin_number
    departure_date = data_invoice.fecha_salida
    balance = data_booking.balance
    desposit_due_date = data_invoice.desglose_passenger_data
    passenger_data_str = data_invoice.passenger_data
    booking_context = data_invoice.booking_context
    itin_cd = get_itin_cd(booking_context)

    fecha_regreso_str = data_invoice.fecha_regreso
    departure_date_str = data_invoice.fecha_salida

    formatted_date3 = create_date.strftime('%Y-%m-%d %H:%M')
    fromatted_date4 = last_payment_date.strftime('%Y-%m-%d %H:%M')

    fecha_regreso1 = datetime.strptime(fecha_regreso_str, "%Y-%m-%d").date()
    departure_date1 = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
    night = (fecha_regreso1 - departure_date1).days

    itineraries = Itinerary.objects.filter(
        Q(cruise_id=cruceroId) &
        Q(itinerary_cd=itin_cd)
    )

    desglose_passenger_data = data_invoice.desglose_passenger_data

    try:
        json_data = json.loads(desglose_passenger_data)

        deposit_due_date_str = json_data['booking_info']['deposit_due_date']
        deposit_due_date = parse_date(deposit_due_date_str)
        formatted_date = format_date1(deposit_due_date)

        final_payment_date_str = json_data['booking_info']['final_payment_date']
        final_payment_date = parse_date(final_payment_date_str)
        formatted_final_payment_date = format_date1(final_payment_date)

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        print("Error parsing date information:", e)
        formatted_date = ""
        formatted_final_payment_date = ""


    try:
        cabin_categories = json.loads(data_invoice.cabin_categories)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        cabin_categories = {}

    if isinstance(cabin_categories, dict) and len(cabin_categories) > 0:
        cabin_type_name = list(cabin_categories.keys())[0]
    else:
        cabin_type_name = None


    try:
        cabin_categories = json.loads(data_invoice.cabin_categories)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        cabin_categories = {}

    if isinstance(cabin_categories, dict) and len(cabin_categories) > 0:
        cabin_type_name = list(cabin_categories.keys())[0]
    else:
        cabin_type_name = None

    fecha_actual = datetime.now().strftime("%Y%m%d")

    if not xml_content or not passenger_data:
        return render(request, 'error.html', {'mensaje_error': 'Datos de sesión incompletos.'})

    booking_info, charge_details = parse_json_response(xml_content)


    fecha_actual = datetime.now().strftime("%Y%m%d")


    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"TVT_{fecha_actual}_{booking_no}.pdf")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=20, leftMargin=10, rightMargin=10, bottomMargin=20)


    def add_header(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(8.0 * inch, 10.8 * inch, f"TVT-{unique_id}")
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='header', frames=[frame], onPage=add_header)
    doc.addPageTemplates([template])


    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterHeading', alignment=1))
    styles.add(ParagraphStyle(name='RightHeading', alignment=2))

    logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo_oficial1.png')

    warning_text = "WARNING: This document is not a ticket nor an invoice. It is issued once the booking is confirmed and following each change."
    warning_style = ParagraphStyle(
        'WarningStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=12,
        alignment=1,
        textColor=light_aqua_blue,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    warning_paragraph = Paragraph(warning_text, warning_style)

    card_data = [[warning_paragraph]]

    card_table = Table(
        card_data,
        colWidths=[0.95 * inch * 8.5],
        rowHeights=[None],
        style=[
            ('BACKGROUND', (0, 0), (-1, -1), None),
            ('BOX', (0, 0), (-1, -1), 0.5, black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]
    )

    elements.append(card_table)
    elements.append(Spacer(1, 0.6 * inch))


    if os.path.exists(logo_path):
        logo = Image(logo_path, 1.7 * inch, 0.9 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
    else:
        error_message = Paragraph(f"<b>Logo no encontrado en la ruta:</b> {logo_path}")
        elements.append(error_message)

    elements.append(Spacer(1, 0.2 * inch))

    invoice_info_style = ParagraphStyle(
        'InvoiceInfoStyle',
        parent=styles['Normal'],
        fontSize=28,
        leading=20,
        alignment=1,
        fontName='Helvetica',
        spaceBefore=20,
        textColor=black,
    )

    invoice_info_style1 = ParagraphStyle(
        'InvoiceInfoStyle1',
        parent=styles['Normal'],
        fontSize=16,
        leading=20,
        alignment=1,
        fontName='Helvetica',
        spaceBefore=20,
        textColor=black,
    )


    justified_style = ParagraphStyle(
        name="Justified",
        parent=getSampleStyleSheet()['Normal'],
        alignment=TA_JUSTIFY,
        leading=12,
        spaceAfter=10,
        fontSize=10,
    )

    ship_name = crucero
    image_ship_path = format_ship_image_path(ship_name)
    cabin_image_path = format_cabin_image_path(ship_name, cabin_type_name)
    logo_path = logo_ship(ship_name)

    ship_image = Image(image_ship_path, 1.5 * inch, 1 * inch) if os.path.exists(image_ship_path) else "Imagen no disponible"
    cabin_image = Image(cabin_image_path, 1.5 * inch, 1 * inch) if os.path.exists(cabin_image_path) else cabin_type


    items_list = request.session.get('items_list', [])
    items_display = ', '.join(items_list) if items_list else 'No packages included'

    experiencia_list = request.session.get('experiencia_list', [])
    experiencia_display = '.<br/>'.join([desc_long for _, desc_long in experiencia_list if desc_long]) if experiencia_list else 'No experience descriptions'
    experiencia_paragraph = Paragraph(experiencia_display, justified_style)


    if os.path.exists(logo_path):
        logo_image = Image(logo_path, 1.0 * inch, 0.7 * inch)
    else:
        logo_image = ship_name


    payment_receive = request.session.get('payment_amount', 0)
    booking_charges = data_invoice.total
    balance_due =  float(booking_charges) - float(payment_receive)
    url_policy = "https://thatvacation.com/static/terms_conditions/msc_terminos.pdf"


    styles = getSampleStyleSheet()
    hyperlink_style = styles['Normal']
    hyperlink_style.fontName = 'Helvetica'
    hyperlink_style.textColor = colors.blue
    hyperlink_style.fontSize = 10

    link_text = f'<a href="{url_policy}">Click here</a>'
    link_paragraph = Paragraph(link_text, hyperlink_style)


    booking_details_data = [
        [""],
        [f"Booking #: {booking_no}", f"Created: {formatted_date3}", logo_image],
        ["Quantity Travel:", total_travelers, ""],
        ["Booking Charges:", booking_charges, ""],
        ["Deposit Amount Due:", deposit_amount_due, ""],
        ["Payments Received:", payments_received, ""],
        ["Balance:", balance, ""],
        ["Last Payment Date", fromatted_date4, ""],
        ["Deposit Due Date:", deposit_due_date_str, ""],
        ["Final Payment Date:", final_payment_date_str, ""],
        ["Cancellation policy ", link_paragraph],
        [""],
        ["Experience:", items_display, ""],
        [""],
        ["Package Included:", experiencia_paragraph, ""],
        [""],
        [""],
        [""],
        ["Ship Name:", ship_name, ship_image, ""],
        [""],
        ["Cabin Type:", cabin_type_name, cabin_image],
        ["Cabin Number:", cabin_number, ""],
        ["Night:", night, ""],
        ["Departure Date:", departure_date, ""],
        ["Return Date:", fecha_regreso, ""],
        [""],
    ]



    booking_details = Table(booking_details_data, colWidths=[1.5 * inch, 4.8 * inch, 1 * inch])
    booking_details.setStyle(TableStyle([
        ('SPAN', (0, 0), (2, 0)),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGNMENT', (0, 0), (-1, 0), 'LEFT'),

        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGNMENT', (2, 10), (2, 11), 'CENTER'),
        ('VALIGN', (2, 10), (2, 11), 'MIDDLE'),
    ]))
    elements.append(booking_details)
    elements.append(Spacer(1, 0.20 * inch))

    header_style = ParagraphStyle(
        name='HeaderStyle',
        parent=styles['Heading3'],
        fontSize=14,
        alignment=1,
        spaceAfter=20,
        textColor=light_aqua_blue,
        fontName='Helvetica-Bold'
    )

    itinerario_reorganizado = []
    for idx, itinerary in enumerate(itineraries):
        port_name = itinerary.departure_port_name or itinerary.arrival_port_name
        departure_time = itinerary.departure_time or "N/A"
        arrival_time = itinerary.arrival_time or "N/A"

        departure_time_clean = format_time_invoice(departure_time) if departure_time != "N/A" else ""
        arrival_time_clean = format_time_invoice(arrival_time) if arrival_time != "N/A" else ""

        if port_name == "At sea":
            formatted_line = f"Day {idx + 1}: At sea"
        else:
            if idx == 0:
                if departure_time_clean:
                    formatted_line = f"Day {idx + 1}: {port_name} Departure: {departure_time_clean}"
                else:
                    formatted_line = f"Day {idx + 1}: {port_name}"
            else:
                time_info = []
                if arrival_time_clean:
                    time_info.append(f"Arrival: {arrival_time_clean}")
                if departure_time_clean:
                    time_info.append(f"Departure: {departure_time_clean}")
                time_info_str = " - ".join(time_info) if time_info else "No times available"
                formatted_line = f"Day {idx + 1}: {port_name} {time_info_str}"

        itinerario_reorganizado.append({
            'dia': idx + 1,
            'port_name': port_name.strip(),
            'departure_time': departure_time_clean.strip(),
            'arrival_time': arrival_time_clean.strip(),
            'arrival_port_name': itinerary.arrival_port_name,
            'arrival_day': itinerary.arrival_day,
            'formatted_line': formatted_line
        })

    if itinerario_reorganizado:
        last_objects_itinerary = itinerario_reorganizado[-1]
    else:
        last_objects_itinerary = None

    itinerario_lines = [item['formatted_line'] for item in itinerario_reorganizado]

    last_itinerary_text = ""
    if last_objects_itinerary:
        last_itinerary_text = (
            f"<br />"
            f"Day {last_objects_itinerary['arrival_day']}: {last_objects_itinerary['arrival_port_name']} Arrival: {last_objects_itinerary['arrival_time']}"
        )

    itinerario_text = "<br />".join(itinerario_lines)
    if last_itinerary_text:
        itinerario_text += f"{last_itinerary_text}"

    itinerario_paragraph = Paragraph(itinerario_text, justified_style)

    elements.append(Paragraph("Ship Itinerary", header_style))
    elements.append(Spacer(1, 0.20 * inch))
    elements.append(itinerario_paragraph)
    elements.append(Spacer(1, 0.20 * inch))

    elements.append(PageBreak())

    charge_totals_json = data_invoice.desglose_passenger_data
    charge_totals = json.loads(charge_totals_json)

    charge_details_table_data = [['Passenger', 'Charge Type', 'Description', 'Amount']]
    grand_total = 0.00
    total_passenger_indices = []

    for person_no, data in charge_totals.get('charge_details', {}).items():
        total_srn = 0.0
        total_cab = 0.0
        total_chd = 0.0
        total_pch = 0.0

        for detail in data['details']:
            charge_type = detail['type']
            amount = float(detail['amount'])
            if charge_type == 'SRN':
                total_srn += amount
            elif charge_type == 'CAB':
                total_cab += amount
            elif charge_type == 'CHD':
                total_chd += amount
            elif charge_type == 'PCH':
                total_pch += amount

        total_passenger = total_cab + total_chd + total_srn + total_pch

        if total_cab > 0:
            charge_details_table_data.append([
                person_no,
                'CAB',
                'Cabin Charges',
                f"${total_cab + total_srn:.2f}"
            ])

        if total_chd > 0:
            charge_details_table_data.append([
                person_no,
                'CHD',
                'Child Cabin Charges',
                f"${total_chd + total_srn:.2f}"
            ])

        if total_pch > 0:
            charge_details_table_data.append([
                person_no,
                'PCH',
                'Port Charge & Tax',
                f"${total_pch:.2f}"
            ])

        charge_details_table_data.append([
            person_no,
            'Total Passenger',
            '-',
            f"${total_passenger:.2f}"
        ])
        total_passenger_indices.append(len(charge_details_table_data) - 1)
        grand_total += total_passenger

    charge_details_table_data.append([
        '',
        'Total to pay',
        '',
        f"${grand_total:.2f}"
    ])

    charges_table = Table(charge_details_table_data, colWidths=[1 * inch, 2 * inch, 3 * inch, 2 * inch])
    charges_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (-1, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (-1, -1), (-1, -1), colors.black),
        ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
    ]))

    for index in total_passenger_indices:
        charges_table.setStyle(TableStyle([
            ('BACKGROUND', (0, index), (-1, index), colors.lightgrey),
            ('TEXTCOLOR', (0, index), (-1, index), colors.black),
            ('FONTNAME', (0, index), (-1, index), 'Helvetica-Bold'),
        ]))

    elements.append(charges_table)
    elements.append(Spacer(1, 0 * inch))


    try:
        passenger_data = json.loads(passenger_data_str)

        invoice_info_style1 = ParagraphStyle(
            'InvoiceInfoStyle1',
            parent=styles['Normal'],
            fontSize=12,
            leading=20,
            alignment=1,
            fontName='Helvetica',
            spaceBefore=20,
            textColor=black,
        )

        for i, passenger in enumerate(passenger_data):
            if i == 0:
                invoice_info_paragraph = Paragraph(f"<p>Passenger # {i + 1}</p>", invoice_info_style1)
                booking_details_data_travel = [
                    [invoice_info_paragraph],
                    ["Full Name", f"{passenger['first_name']} {passenger['last_name']}"],
                    ["Email & Phone Number", f"{passenger['email']}", f"+{passenger['telephone_no']}"],
                    ["Date of Birth", f"{passenger['date_of_birth']}", "-"],
                    ["Gender & Title", f"{passenger['gender']}", "Male" if passenger['gender'] == 'M' else "Female" if passenger['gender'] == 'F' else "-"],
                    ["City & State", f"{passenger['city']}, {passenger['state_province']}", "-"],
                ]
            else:
                invoice_info_paragraph = Paragraph(f"<p>Passenger # {i + 1}</p>", invoice_info_style1)
                booking_details_data_travel = [
                    [invoice_info_paragraph],
                    ["Full Name", f"{passenger['first_name']} {passenger['last_name']}"],
                    ["Date of Birth", f"{passenger['date_of_birth']}", "-"],
                    ["Gender & Title", f"{passenger['gender']}", "Male" if passenger['gender'] == 'M' else "Female" if passenger['gender'] == 'F' else "-"],
                ]

            booking_details = Table(booking_details_data_travel, colWidths=[2 * inch, 4 * inch, 2 * inch])
            booking_details.setStyle(TableStyle([
                ('SPAN', (0, 0), (2, 0)),
                ('BACKGROUND', (0, 0), (-1, 0), lighter_aqua_blue1),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGNMENT', (0, 0), (-1, 0), 'LEFT'),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('GRID', (0, 1), (-1, -1), 0.25, colors.black),
            ]))
            elements.append(booking_details)
            elements.append(Spacer(1, 0 * inch))

    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")

    elements.append(PageBreak())

    documentation_style = ParagraphStyle('DocumentationStyle', parent=styles['Normal'], fontSize=10, leading=12, spaceBefore=10, spaceAfter=10, textColor=colors.black, alignment=TA_JUSTIFY, leftIndent=3, rightIndent=3)
    text_booking_details = Paragraph("""
        <p>
        <b>Online Check-In: Download APP. "Cruise line"</b><br/>
        Guests are requested to complete their Online Check-In form at least 21 days and up to 3 days prior to your vacation start date. Guests who have not completed their online Check-In forms at 3 days prior to their vacation start date are required to complete the Check-In process at the pier at least 2 hours prior to the departure time noted on their cruise documents.<br />
        <br />
        <b>Warning:</b> <br />
        The balance due must be paid in full by the final payment date listed above to prevent your booking from cancelling.
        <br />
        <br />
        <b>Important:</b> <br />
        *A change fee of $100 USD per guest will apply for ship or sail date changes.<br />
        *Within 24 hours you will receive your booking confirmation
        </p>
        <br/>
        <br />
        <b>Documentation and Immigration Requirements.</b><br/>
        Guests are highly encouraged to travel with a valid passport, even when not required. <br/>
        <br/>
        For your protection, we recommend that your passport expiration date does not occur within six (6) months of the sailing return date.<br/>
        <br/>
        Some foreign ports of call require a visa. Please contact the Embassy (Consular Services) of each country on your sailing itinerary or the visa service of your choice for specific
        visa requirements, information, forms and fees for your nationality. That Vacation Travel Corp. suggests the visa provider, CIBT at <link href="https://www.visacentral.com" color="blue">www.visacentral.com</link>.<br/>
        <br/>
        The spelling of the guest(s) name as booked for a cruise must match exactly as their valid passport or proof of citizenship / identification during ship check-in formalities. <br/>
        <br/>
        Certain countries may have specific travel requirements for your itinerary.<br/>
        <br/>
        All guests (including children) must present a valid passport when sailing on U.S. Open Loop voyages. These are voyages that commence in a U.S. port, travel within the
        Western Hemisphere, and end at a different U.S. port. When traveling on these sailings, please take extra caution in understanding the specific documentation
        requirements.<br/>
        <br/>
        All guests (including children) require specific travel documents that may include either a passport or other documentation, such as a government-issued birth certificate and
        laminated government issued picture ID denoting photo, name and date of birth, when traveling on U.S. Closed Loop voyages. These are voyages that commence
        and end in the same U.S. port without leaving the western hemisphere. Please note that Baptismal papers, hospital certificates of birth, voter registration cards or
        Social Security cards are not considered proof of citizenship.<br/>
        <br/>
        Should the last names of the parent and minor child traveling with them differ, the parent is required to present the child's valid passport and visa (if required) and the child's
        birth certificate (original, a notarized copy or a certified copy). The name of the parent(s) and the child must be linked through legal documentation.<br/>
        <br/>
        Adults who are not the parent or legal guardian of a minor traveling with them must present an original notarized letter signed by the child's parent(s), authorizing the adult to
        take the child on the specific cruise, supervise the child and allow emergency medical treatment to be administered.<br/>
        <br/>
        Guests on consecutive sailings must ensure they have the proper travel documents for their entire cruise vacation and for any port within their itinerary(s).
        <br/>
        <b>• Age Restrictions:</b><br/>
        This cruise line requires that passengers younger than 21 years old be accompanied by an adult 21 years or older in the same cabin.
        Infants must be at least 3 months old as of the first day of the cruise, with doctor’s approval letter that they can sail. In the event Passenger intends to bring onboard any child under the age of 12 months, the Company recommends seeking medical advice from the child’s physician confirming such child’s fitness to travel on an international ocean voyage.
        <br/>
        <b>• Pregnancy Restrictions:</b><br/>
        Pregnant women are highly recommended to seek medical advice prior to travel at any stage of their pregnancy. The Carrier cannot for safety reasons carry pregnant Passengers of 24 weeks or more by the end of the cruise. The Carrier reserves the right to request a medical certificate at any stage of pregnancy and to refuse passage if the Carrier and/or the Master are not satisfied that the Passenger will be safe during the passage.
        <br/>
        <br/>
        <b>Terms & Condition - Privacy Policy</b><br />

    """, documentation_style)
    elements.append(text_booking_details)
    elements.append(Spacer(1, 0.25 * inch))


    doc.build(elements, onFirstPage=footer, onLaterPages=footer)
    buffer.seek(0)
    pdf_content = buffer.getvalue()
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="TVT{fecha_actual}{booking_no}.pdf"'


    request.session['pdf_path'] = pdf_path
    request.session['booking_info'] = booking_info
    request.session['fecha_actual'] = fecha_actual
    request.session['crucero'] = crucero
    request.session['total_travelers'] = total_travelers
    request.session['balance_due'] = balance_due
    request.session['payment_receive'] = payment_receive
    request.session['passenger_data'] = passenger_data
    request.session['items_list'] = items_list
    request.session['experiencia_list'] = experiencia_list
    request.session['grand_total'] = grand_total

    user_email = request.user.email
    passenger_email = passenger_data[0]['email']

    subject = "Your Cruise Booking Invoice"
    message = "Please find attached your booking invoice."
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email],bcc=['thatvacationtravel@gmail.com'] )

    email.attach_file(pdf_path)
    email.send()

    return success_postpay(request, booking_no)



def success_postpay(request, booking_no):
    data_booking = get_object_or_404(Booking, booking_number=booking_no)
    data_invoice = get_object_or_404(InvoiceCustomer, booking_no=booking_no)

    pdf_path = request.session.get('pdf_path')
    booking_info = request.session.get('booking_info')
    fecha_actual = request.session.get('fecha_actual')
    crucero = request.session.get('crucero')
    total_travelers = request.session.get('total_travelers')
    balance_due = request.session.get('balance_due')
    payment_receive = request.session.get('payment_receive')
    passenger_data = request.session.get('passenger_data')
    items_list = request.session.get('items_list')
    experiencia_list = request.session.get('experiencia_list')
    grand_total = request.session.get('grand_total')

    departure = data_invoice.fecha_salida
    return_day = data_invoice.fecha_regreso
    balance = data_booking.balance
    total_paid = data_booking.total_paid
    crucero = data_booking.unique_id

    context = {
        'pdf_path': pdf_path,
        'booking_info': booking_info,
        'fecha_actual': fecha_actual,
        'crucero': crucero,
        'total_travelers': total_travelers,
        'balance': balance,
        'payment_receive': payment_receive,
        'passenger_data': passenger_data,
        'items_list': items_list,
        'experiencia_list': experiencia_list,
        'grand_total': grand_total,
        'departure':departure,
        'return_day':return_day,
        'total_paid':total_paid,
    }

    return render(request, 'success.html', context)



def cabins(request, crucero_id, priceVariable):
    crucero = Cruise.objects.filter(cruiseID=crucero_id).first()
    cruises = Cruise.objects.filter(cruiseID=crucero_id)


    price_variable = priceVariable

    if not crucero:
        return render(request, 'error.html', {'message': 'Crucero no encontrado.'})

    prices_by_category = {}
    for cruise in cruises:
        category = cruise.category
        price = {
            'oneAdult': str(cruise.oneAdult),
            'twoAdults': str(cruise.twoAdult),
            'threeAdults': str(cruise.threeAdult),
            'fourAdults': str(cruise.fourAdult),

        }
        if category not in prices_by_category:
            prices_by_category[category] = price_variable
        else:

            for key in price_variable:
                if price_variable[key] and (not prices_by_category[category][key] or float(price_variable[key]) < float(prices_by_category[category][key])):
                    prices_by_category[category][key] = price_variable[key]

    lowest_prices_by_category = {}
    for category, price_variable in prices_by_category.items():
        if not lowest_prices_by_category:
            lowest_prices_by_category = price_variable
        else:
            for key, value in price_variable.items():
                if value != 'None' and (key not in lowest_prices_by_category or lowest_prices_by_category[key] == 'None' or float(value) < float(lowest_prices_by_category[key])):
                    lowest_prices_by_category[key] = value


    categorized_deck_ranges = defaultdict(set)
    guaranteed_cabins = defaultdict(lambda: False)

    cabinas = Cabin.objects.filter(ship_code=crucero.shipCd)

    for cabina in cabinas:
        cabin_type = cabina.category[0]
        if cabina.cabin_number.startswith('G'):
            guaranteed_cabins[cabin_type] = True
        else:
            deck_number = int(cabina.cabin_number[:2])
            categorized_deck_ranges[cabin_type].add(deck_number)

    subranges = [(1, 2), (3, 5), (6, 9), (10, 12), (13, 15), (16, 18)]
    categorized_subranges = defaultdict(list)

    for cabin_type, deck_numbers in categorized_deck_ranges.items():
        for start, end in subranges:
            subrange = set(range(start, end + 1))
            intersected = subrange.intersection(deck_numbers)
            if intersected:
                categorized_subranges[cabin_type].append(f"{min(intersected)}-{max(intersected)}")

        if guaranteed_cabins[cabin_type]:
            categorized_subranges[cabin_type].append('Guaranteed')

    category_labels = {
        'I': 'Inside',
        'O': 'Ocean View',
        'B': 'Balcony',
        'S': 'Suite',
        'Y': 'Suite',
    }

    display_data = {
        category_labels.get(cabin_type, 'Unknown'): subranges
        for cabin_type, subranges in categorized_subranges.items()
    }

    cabin_numbers_by_range = defaultdict(lambda: defaultdict(list))
    for cabina in cabinas.exclude(cabin_number__startswith='G'):
        deck_number = int(cabina.cabin_number[:2])
        for start, end in subranges:
            if start <= deck_number <= end:
                subrange_key = f"{start}-{end}"
                cabin_numbers_by_range[cabina.category[0]][subrange_key].append(cabina.cabin_number)

    return render(request, 'cabinas.html', {
        'crucero': crucero,
        'display_data': display_data,
        'prices_by_category': prices_by_category,
        'cabin_numbers_by_range': cabin_numbers_by_range,
        'lowest_prices_by_category': lowest_prices_by_category,
    })



def calcula_hash_sha256(cadena):
    return hashlib.sha256(cadena.encode()).hexdigest()

def search_cruises(request):
    cruise_data = []
    if request.method == 'POST':
        form = CruiseSearchForm1(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['departure_date']
            end_date = form.cleaned_data['departure_end_date']
            sailingPort = form.cleaned_data['destination']

            cruises = Cruise.objects.filter(sailingDate__range=(start_date, end_date), sailingPort=sailingPort)
            cruise_data = [{'cruiseID': cruise.cruiseID,
                            'sailingDate': cruise.sailingDate.strftime('%Y-%m-%d'),
                            'shipName': cruise.shipName,
                            'itinDesc': cruise.itinDesc,
                            'nights': cruise.nights,
                            'sailingPort': cruise.sailingPort,
                            'oneAdult': cruise.oneAdult,
                            'fareStartDate': cruise.fareStartDate,
                            'fareEndDate': cruise.fareEndDate,
                            'priceType':cruise.priceType,
                            'category':cruise.category,
                            'fareCode': cruise.fareCode,
                            }
                            for cruise in cruises
                          ]

    else:
        form = CruiseSearchForm1()

    return render(request, 'buscar_crucero2.html', {'form': form, 'cruise_data': cruise_data})




@csrf_exempt
@login_required
def buscar_cruceros(request):
    if request.user.is_authenticated and not request.user.aprobacion:
        return redirect('index')
    if request.method == 'POST':
        form = CruiseSearchForm1(request.POST)
        if form.is_valid():
            departure_date = form.cleaned_data['departure_date']
            formatted_departure_date = departure_date.strftime('%d/%m/%Y')
            departure_end_date = form.cleaned_data['departure_end_date']
            formatted_end_departure_date = departure_end_date.strftime('%d/%m/%Y')
            destination = form.cleaned_data['destination']
            adultos = form.cleaned_data['adultos']
            ninos = form.cleaned_data['ninos']

            url = 'https://wsrv3.msccruises.com/mscbee/services/searchcruises/searchcruisesdetV1/'
            password_hash = calcula_hash_sha256("Mscx1x2x3!")

            headers = {
                    'Content-Type': 'text/xml',
                    'AgencyID': 'US159929',
                    'True-Client-IP': '10.0.0.50',
                    'UserID': 'OTA3-US159929',
                    'Password': password_hash,
                    'AgentID': 'US159929',
                    }

            xml_data = f'''
                <DtsSearchCruisesV1 xmlns="DTS">
                    <ShipCd/>
                    <DepStartDate>{formatted_departure_date}</DepStartDate>
                    <DepEndDate>{formatted_end_departure_date}</DepEndDate>
                    <SailingDuration/>
                    <MaxSailingDuration/>
                    <LanguageCd>ENG</LanguageCd>
                    <OfficeCd>USA</OfficeCd>
                    <MktCd>USA</MktCd>
                    <CurrcyCd>USD</CurrcyCd>
                    <AgentId>US159929</AgentId>
                    <BookingChannel>XML</BookingChannel>
                    <BudgetRange>0-5000</BudgetRange>
                    <Flight>N</Flight>
                    <NoofAdults>{adultos}</NoofAdults>
                    <NoofChildren>{ninos}</NoofChildren>
                    <PaxType/>
                    <Discounts/>
                    <PhysicallyChallenged>No</PhysicallyChallenged>
                    <PortCD>{destination}</PortCD>
                    <Sort>C</Sort>
                </DtsSearchCruisesV1>
            '''
            try:
                response = requests.post(url, headers=headers, data=xml_data)

                if response.status_code == 200:
                    parser = etree.XMLParser(ns_clean=True, recover=True)
                    root = etree.fromstring(response.content, parser=parser)
                    namespaces = {
                        'dts': 'DTS',
                        'xs': 'http://www.w3.org/2001/XMLSchema-instance',
                    }

                    itineraries = root.xpath('.//dts:Itinerary', namespaces=namespaces)
                    cruise_data = []

                    for itinerary in itineraries:
                        best_price = itinerary.xpath('.//dts:Cruises', namespaces=namespaces)[0]
                        best_price1 = itinerary.xpath('.//dts:BestPrice', namespaces=namespaces)[0]
                        best_price2 = itinerary.xpath('.//dts:ItemDetails', namespaces=namespaces)[0]

                        puerto_desemb = best_price.xpath('dts:DisembkPort/text()', namespaces=namespaces)[0]
                        cabin_avail = best_price.xpath('dts:CabinsAvailable/text()', namespaces=namespaces)[0]
                        cruise_id = best_price.xpath('dts:CruiseId/text()', namespaces=namespaces)[0]
                        shipname = best_price.xpath('dts:ShipName/text()', namespaces=namespaces)[0]
                        itinerario = itinerary.xpath('dts:ItinDesc/text()', namespaces=namespaces)[0]
                        precio = best_price1.xpath('dts:BestPriceCabinPrice/text()', namespaces=namespaces)[0]
                        detalles = best_price2.xpath('dts:ItemDescription/text()', namespaces=namespaces)[0]

                        regreso_str = best_price.xpath('dts:ArrivalDate/text()', namespaces=namespaces)[0]
                        regreso = datetime.strptime(regreso_str, '%Y-%m-%d').date()
                        salida_str = best_price.xpath('dts:DepartureDate/text()', namespaces=namespaces)[0]
                        salida = datetime.strptime(salida_str, '%Y-%m-%d %H:%M:%S.%f').date()
                        dias = (regreso - salida).days

                        category_list = best_price.xpath('dts:Category/text()', namespaces=namespaces)[0]
                        itemcode = best_price2.xpath('dts:ItemCode/text()', namespaces=namespaces)[0]
                        itemtype = best_price2.xpath('dts:ItemTypeCode/text()', namespaces=namespaces)[0]
                        packagecode = best_price2.xpath('dts:PackageCode/text()', namespaces=namespaces)[0]
                        price_type = best_price.xpath('dts:PriceType/text()', namespaces=namespaces)[0]


                        cruise_data.append({
                            'puerto_desemb': puerto_desemb,
                            'cabin_avail': cabin_avail,
                            'cruise_id': cruise_id,
                            'shipname': shipname,
                            'itinerario': itinerario,
                            'precio': precio,
                            'regreso': regreso,
                            'salida': salida,
                            'dias': dias,
                            'detalles': detalles,
                            'categoria': category_list,
                            'itemcode':itemcode,
                            'itemtype':itemtype,
                            'packagecode':packagecode,
                            'price_type':price_type
                        })

                    return render(request, 'resultados.html', {'cruise_data': cruise_data, 'root':response.content})
                else:
                    error_details = {
                    'status_code': response.status_code,
                    'response_headers': response.headers,
                    'response_body': response.text
                }
                return render(request, 'error.html', {'error_details': error_details})

            except requests.exceptions.RequestException as e:
                return render(request, 'error.html', {'mensaje_error': str(e)})
    else:
        form = CruiseSearchForm1()

    return render(request, 'buscar_crucero2.html', {'form': form})



def categorizar_cabinas(available_cabins, ns):
    categorias = {
        'Inside': [],
        'Ocean_view': [],
        'Balcon': [],
        'Suit': []
    }

    for available_cabin in available_cabins:
        cabin_number = available_cabin.find('ns1:CabinNo', namespaces=ns).text
        cabin_name = available_cabin.find('ns1:DeckName', namespaces=ns).text
        category_code_element = available_cabin.find('ns1:CategoryCode', namespaces=ns)


        if category_code_element is not None:
            category_code = category_code_element.text
        else:
            continue

        if category_code in ('IB', 'IR1', 'IR2', 'I2','I1'):
            categorias['Inside'].append({'number': cabin_number, 'name': cabin_name})
        elif category_code in ('BB', 'BR1', 'BR2', 'BR3', 'BR4', 'BA', 'BBL'):
            categorias['Balcon'].append({'number': cabin_number, 'name': cabin_name})
        elif category_code in ('OB', 'OR1', 'OBS'):
            categorias['Ocean_view'].append({'number': cabin_number, 'name': cabin_name})
        elif category_code in ('SM', 'SL1', 'SLT', 'SLW', 'SX', 'YC1', 'YCP'):
            categorias['Suit'].append({'number': cabin_number, 'name': cabin_name})

    return categorias



def seleccion_cabinas(request, cruise_id, itemcode, itemtype, packagecode):

    if request.method == 'POST':
        pax_type = request.POST.get('paxType', 'HONEY')
        no_adults = request.POST.get('noAdults', '2')
        no_children = request.POST.get('noChildren', '2')
        child_age = request.POST.get('childAge', '13,0')

        promotion_code = request.POST.get('promotionCode', 'FA1712ITEAF00')

    else:
        pax_type = 'HONEY'
        no_adults = '2'
        no_children = '2'
        child_age = '13,0'
        promotion_code = 'FA1712ITEAF00'

    category_codes = ['IB','I2','I1','IR1', 'IR2', 'BB','BBL', 'BR1', 'BR2', 'BR3', 'BR4', 'BA', 'OB', 'OR1', 'SM', 'SL1', 'SLT', 'SLW', 'SX', 'YC1', 'YCP']

    categorias = {
        'Inside': [],
        'Ocean_view': [],
        'Balcon': [],
        'Suit': []
    }


    itemcode = itemcode
    itemtype = itemtype
    packagecode = packagecode
    password_hash = calcula_hash_sha256("Mscx1x2x3!")
    cabin_headers = {
        'Content-Type': 'text/xml',
        'AgencyID': 'US159929',
        'True-Client-IP': '10.0.0.50',
        'UserID': 'OTA3-US159929',
        'Password': password_hash,
        'AgentID': 'US159929',
    }

    for category_code in category_codes:
        cabin_xml_data = f'''
            <DtsCruiseCabinAvailabilityRequest xmlns="DTS">
                <BookingContext>
                    <AdvertisingSource />
                    <BookingContactName>1</BookingContactName>
                    <LoyalityCardMemberLevel />
                    <PaxType>{pax_type}</PaxType>
                    <NoAdults>{no_adults}</NoAdults>
                    <NoChildren>{no_children}</NoChildren>
                    <ChildAge>{child_age}</ChildAge>
                </BookingContext>
                <CruiseComponent>
                    <CruiseID>{cruise_id}</CruiseID>
                    <CategoryCode>{category_code}</CategoryCode>
                    <PromotionCode>{promotion_code}</PromotionCode>
                </CruiseComponent>
            </DtsCruiseCabinAvailabilityRequest>
        '''
        try:
            cabin_response = requests.post('https://wsrv3.msccruises.com/mscbee/services/cabin/getcabins/', headers=cabin_headers, data=cabin_xml_data.encode('utf-8'))
            cabin_response.raise_for_status()
            cabin_root = ET.fromstring(cabin_response.content)
            ns = {'ns1': 'DTS'}
            available_cabins = cabin_root.findall('.//ns1:AvailableCabin', namespaces=ns)
            for available_cabin in available_cabins:
                cabin_number = available_cabin.find('ns1:CabinNo', namespaces=ns).text
                cabin_name = available_cabin.find('ns1:ShipLocationDesc', namespaces=ns).text
                deck_number = available_cabin.find('ns1:DeckCode', namespaces=ns).text

                if category_code in ('IB','IR1','IR2'):
                    categorias['Inside'].append({'number': cabin_number, 'name': cabin_name, 'deck': deck_number, 'category_code': category_code})

                elif category_code in ('BB','BBL', 'BR1', 'BR2', 'BR3', 'BR4', 'BA'):
                    categorias['Balcon'].append({'number': cabin_number, 'name': cabin_name, 'deck': deck_number, 'category_code': category_code})
                elif category_code in ('OB', 'OR1'):
                    categorias['Ocean_view'].append({'number': cabin_number, 'name': cabin_name, 'deck': deck_number, 'category_code': category_code})
                elif category_code in ('SM', 'SL1', 'SLT', 'SLW', 'SX', 'YC1', 'YCP'):
                    categorias['Suit'].append({'number': cabin_number, 'name': cabin_name, 'deck': deck_number, 'category_code': category_code})
        except requests.exceptions.RequestException as e:

            pass

    return render(request, 'seleccion_cabinas.html', {'categorias_cabinas': categorias, 'cruise': cruise_id, 'cabin_root':cabin_root, 'itemcode': itemcode, 'itemtype':itemtype, 'packagecode':packagecode})



def obtener_cabinas(cruise_id, categoria):
    password_hash = calcula_hash_sha256("Mscx1x2x3!")
    pax_type = 'HONEY'
    no_adults = '2'
    no_children = '2'
    child_age = '13,0'
    promotion_code = 'FA1712ITEAF00'

    cabin_headers = {
        'Content-Type': 'text/xml',
        'AgencyID': 'US159929',
        'True-Client-IP': '10.0.0.50',
        'UserID': 'OTA3-US159929',
        'Password': password_hash,
        'AgentID': 'US159929',
    }

    cabin_xml_data = f'''
        <DtsCruiseCabinAvailabilityRequest xmlns="DTS">
            <BookingContext>
                <AdvertisingSource />
                <BookingContactName>1</BookingContactName>
                <LoyalityCardMemberLevel />
                <PaxType>{pax_type}</PaxType>
                <NoAdults>{no_adults}</NoAdults>
                <NoChildren>{no_children}</NoChildren>
                <ChildAge>{child_age}</ChildAge>
            </BookingContext>
            <CruiseComponent>
                <CruiseID>{cruise_id}</CruiseID>
                <PromotionCode>{promotion_code}</PromotionCode>
            </CruiseComponent>
        </DtsCruiseCabinAvailabilityRequest>
    '''

    try:
        cabin_response = requests.post('https://wsrv3.msccruises.com/mscbee/services/cabin/getcabins/', headers=cabin_headers, data=cabin_xml_data.encode('utf-8'))
        cabin_response.raise_for_status()
        cabin_root = ET.fromstring(cabin_response.content)
        ns = {'ns1': 'DTS'}
        available_cabins = cabin_root.findall('.//ns1:AvailableCabin', namespaces=ns)
        return categorizar_cabinas(available_cabins, ns)[categoria]
    except requests.exceptions.RequestException as e:
        return []


class ObtenerCabinasView(View):
    def get(self, request, *args, **kwargs):
        cruise_id = kwargs.get('cruise_id')
        categoria = kwargs.get('categorias')
        cabinas = obtener_cabinas(cruise_id, categoria)
        data = {
            'cabinas': cabinas
        }
        return JsonResponse(data)



def lock_cabin(cruise_id, cabin_number):
    password_hash = calcula_hash_sha256("Mscx1x2x3!")
    url = 'https://wsrv3.msccruises.com/mscbee/services/cabin/getcabinlock/'
    headers = {
        'AgencyID': 'US159929',
        'True-Client-IP': '10.0.0.50',
        'UserID': 'OTA3-US159929',
        'Password': password_hash,
        'AgentID': 'US159929',
    }

    xml_data = f'''
        <?xml version="1.0" encoding="UTF-8"?>
        <DtsCruiseCabinLockRequestMessage xmlns="DTS">
         <BookingChannel>XML</BookingChannel>
            <CruiseId>{cruise_id}</CruiseId>
            <CabinsToBook>
                <CabinNo>{cabin_number}</CabinNo>
            </CabinsToBook>
        </DtsCruiseCabinLockRequestMessage>
    '''
    return requests.post(url, headers=headers, data=xml_data)




import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render

def cancelation(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        booking_no = request.POST.get('booking_no')
        booking_note = request.POST.get('booking_note')

        if not booking_no or len(booking_no) < 8:
            error_message = 'Número de reserva inválido.'
            return render(request, 'cancelations_forms.html', {'error': error_message})

        url = 'https://wsrv3.msccruises.com/mscbee/services/cancelBooking/doCancelBooking'
        headers = {
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': '0cf43a5e90d824440ea9b809b153dcfb4d5960ecb450442c904c1d28b16d8aa0',
            'AgentID': 'US159929',
        }

        xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
            <DtsCancelBookingRequestMessage xmlns="DTS">
                <BookingContext>
                    <AgencyID>US159929</AgencyID>
                    <BookingContactName>ThatVacation</BookingContactName>
                    <BookingNo>{booking_no}</BookingNo>
                    <BookingChannel>ONL</BookingChannel>
                </BookingContext>
            </DtsCancelBookingRequestMessage>
        '''
        try:
            response = requests.post(url, headers=headers, data=xml_data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_message = f'Error en la solicitud: {str(e)}'
            return render(request, 'cancelations_forms.html', {'error': error_message})

        try:
            root = ET.fromstring(response.content)
            namespace = {'DTS': 'DTS'}

            booking_no_elem = root.find('.//DTS:BookingNo', namespaces=namespace)
            advisory_message_elem = root.find('.//DTS:MessageText', namespaces=namespace)
            booking_status_desc_elem = root.find('.//DTS:BookingStatusDesc', namespaces=namespace)
            total_payments_received_elem = root.find('.//DTS:TotalPaymentsReceived', namespaces=namespace)
            gross_balance_due_elem = root.find('.//DTS:GrossBalanceDue', namespaces=namespace)
            net_balance_due_elem = root.find('.//DTS:NetBalanceDue', namespaces=namespace)

            booking_no = booking_no_elem.text if booking_no_elem is not None else "No disp"
            advisory_message = advisory_message_elem.text if advisory_message_elem is not None else "No disponible"
            booking_status_desc = booking_status_desc_elem.text if booking_status_desc_elem is not None else "No disponible"
            total_payments_received = total_payments_received_elem.text if total_payments_received_elem is not None else "No disponible"
            gross_balance_due = gross_balance_due_elem.text if gross_balance_due_elem is not None else "No disponible"
            net_balance_due = net_balance_due_elem.text if net_balance_due_elem is not None else "No disponible"

        except ET.ParseError:
            error_message = 'Error al procesar la respuesta de la API.'
            return render(request, 'cancelations_forms.html', {'error': error_message})

        booking_entry = Booking.objects.filter(booking_number=booking_no).first()

        if not booking_entry:
            error_message = 'No se encontró la reserva.'
            return render(request, 'cancelations_forms.html', {'error': error_message})

        cancelation_entry = Cancelations(
            booking_note=booking_note,
            booking_no=booking_no,
            booking_status=booking_status_desc,
            total_payments_received=total_payments_received,
            gross_balance_due=gross_balance_due,
            net_balance_due=net_balance_due,
            created_at = booking_entry.created_at
        )
        cancelation_entry.save()

        InvoiceCustomer.objects.filter(booking_no=booking_no).delete()
        Booking.objects.filter(booking_number=booking_no).delete()

        success_message = {
            'booking_no': booking_no,
            'advisory_message': advisory_message,
            'booking_status': booking_status_desc,
            'total_payments_received': total_payments_received,
            'gross_balance_due': gross_balance_due,
            'net_balance_due': net_balance_due,
            'full_response': response.content.decode('utf-8'),
        }

        return render(request, 'success_cancelations.html', {'message': success_message})

    return render(request, 'cancelations_forms.html', {'error': error_message})



@csrf_exempt
def process_payment1(request, booking_no, total):
    booking_no = booking_no
    if request.method == "POST":
        payment_amount = 1.00
        credit_card_code = request.POST.get('credit_card_code')
        credit_card_number = request.POST.get('credit_card_number')
        name_on_credit_card = request.POST.get('name_on_credit_card')
        ccv_code = request.POST.get('ccv_code')
        expiration_month = request.POST.get('expiration_month')
        expiration_year = request.POST.get('expiration_year')

        #url = 'https://wsrv.msccruises.com/upp/proxy/push/1b0159e8ce0fc024'
        url = 'https://wsrv.msccruises.com/upp/proxy/push/b5383d345a695897'
        headers = {
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': '0cf43a5e90d824440ea9b809b153dcfb4d5960ecb450442c904c1d28b16d8aa0',
            'AgentID': 'US159929',
        }

        xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
            <DtsApplyPaymentRequestMessage xmlns="DTS">
                <BookingContext>
                    <AgencyID>US159929</AgencyID>
                    <BookingContactName>gfusita</BookingContactName>
                    <BookingNo>{booking_no}</BookingNo>
                    <BookingChannel>XML</BookingChannel>
                </BookingContext>
                <Payment>
                    <ReceivedFrom>fusco</ReceivedFrom>
                    <PaymentAmount>{payment_amount}</PaymentAmount>
                    <FormOfPaymentCode>CC</FormOfPaymentCode>
                    <DocumentNo/>
                    <ReferenceNo/>
                    <CreditCardInfo>
                        <CreditCardCode>{credit_card_code}</CreditCardCode>
                        <CreditCardNumber>{credit_card_number}</CreditCardNumber>
                        <NameOnCreditCard>{name_on_credit_card}</NameOnCreditCard>
                        <CCVCode>{ccv_code}</CCVCode>
                        <Process>true</Process>
                        <ExpirationDate>
                            <ExpirationMonth>{expiration_month}</ExpirationMonth>
                            <ExpirationYear>{expiration_year}</ExpirationYear>
                        </ExpirationDate>
                        <IssueNum>1</IssueNum>
                    </CreditCardInfo>
                    <ScheduleDue/>
                    <SkipDirecao>true</SkipDirecao>
                </Payment>
            </DtsApplyPaymentRequestMessage>
        '''

        response = requests.post(url, headers=headers, data=xml_data)
        response_xml = response.text

        if response.status_code == 200:
            return JsonResponse({'status': 'success', 'message': response_xml}, status=200)
        else:
            mensaje_error = f"Error in request. Code State: {response.status_code}"
            return JsonResponse({'status': 'error', 'message': mensaje_error}, status=500)
    else:

        return render(request, 'payment_process.html', {'booking_no': booking_no, 'total':total})



@csrf_exempt
def process_payment(request, booking_no, total):
    booking_no = booking_no
    url = 'https://wsrv.msccruises.com/upp/proxy/push/1b0159e8ce0fc024'
    headers = {
            'AgencyID': 'US159929',
            'True-Client-IP': '10.0.0.50',
            'UserID': 'OTA3-US159929',
            'Password': '0cf43a5e90d824440ea9b809b153dcfb4d5960ecb450442c904c1d28b16d8aa0',
            'AgentID': 'US159929',
        }
    xml_data = f'''<?xml version="1.0" encoding="UTF-8"?>
        <DtsApplyPaymentRequestMessage xmlns="DTS">
            <BookingContext>
                <AgencyID>US159929</AgencyID>
                <BookingContactName>gfusita</BookingContactName>
                <BookingNo>{booking_no}</BookingNo>
                <BookingChannel>XML</BookingChannel>
            </BookingContext>
            <Payment>
                <ReceivedFrom>fusco</ReceivedFrom>
                <PaymentAmount>1.00</PaymentAmount>
                <FormOfPaymentCode>CC</FormOfPaymentCode>
                <DocumentNo/>
                <ReferenceNo/>
                <CreditCardInfo>
                    <CreditCardCode>VI</CreditCardCode>
                    <CreditCardNumber>5100001000000030</CreditCardNumber>
                    <NameOnCreditCard>Visa</NameOnCreditCard>
                    <CCVCode>123</CCVCode>
                    <Process>true</Process>
                    <ExpirationDate>
                        <ExpirationMonth>06</ExpirationMonth>
                        <ExpirationYear>2025</ExpirationYear>
                    </ExpirationDate>
                    <IssueNum>1</IssueNum>
                </CreditCardInfo>
                <ScheduleDue/>
                <SkipDirecao>true</SkipDirecao>
            </Payment>
        </DtsApplyPaymentRequestMessage>
        '''
    response = requests.post(url, headers=headers, data=xml_data)
    if response.status_code == 200:
        return JsonResponse(response.status_code, status=200, safe=False)
    else:
            mensaje_error = f"Error en la solicitud. Código de estado: {response.status_code}"
            return JsonResponse({'error': mensaje_error}, status=500)




#---------------enviar correos-----------
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from reservas.forms import EmailForm
from django.template.loader import get_template

from django.shortcuts import get_object_or_404

def enviar_correo_promocional(request):
    # Obtiene el objeto de template_email que quieres actualizar.
    existing_object = get_object_or_404(template_email, id=2)
    year = datetime.now().year
    destino_email = paqueteoferta.objects.all()

    error_message = None
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            recipients = form.cleaned_data['recipients']
            encabezado = form.cleaned_data['encabezado']
            video = form.cleaned_data['video']
            recipient_list = [email.strip() for email in recipients.split(',')]

            existing_object.imagen1 = form.cleaned_data.get('image1') or existing_object.imagen1
            existing_object.imagen2 = form.cleaned_data.get('image2') or existing_object.imagen2
            existing_object.imagen3 = form.cleaned_data.get('image3') or existing_object.imagen3
            existing_object.imagen4 = form.cleaned_data.get('image4') or existing_object.imagen4
            existing_object.imagen5 = form.cleaned_data.get('image5') or existing_object.imagen5
            existing_object.save()

            imagenes = [
                request.build_absolute_uri(existing_object.imagen1.url) if existing_object.imagen1 else '',
                request.build_absolute_uri(existing_object.imagen2.url) if existing_object.imagen2 else '',
                request.build_absolute_uri(existing_object.imagen3.url) if existing_object.imagen3 else '',
                request.build_absolute_uri(existing_object.imagen4.url) if existing_object.imagen4 else '',
                request.build_absolute_uri(existing_object.imagen5.url) if existing_object.imagen5 else '',
            ]

            try:
                for recipient in recipient_list:
                    msg = EmailMultiAlternatives(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [recipient],
                    )
                    msg.content_subtype = "html"
                    html_content = get_template('template_email.html').render({'message': message, 'imagenes': imagenes, 'encabezado':encabezado, 'video':video, 'year':year, 'destino_email': destino_email})
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
            except Exception as e:
                error_message = f"Hubo un error al enviar el correo: {e}"

            if error_message is None:
                return render(request, 'correo_enviado_exitosamente.html')

    else:
        form = EmailForm(initial={

        })

    return render(request, 'send_mail.html', {'form': form, 'error_message': error_message})




def template(request):
    destino_email = paqueteoferta.objects.all()
    year = datetime.now().year
    estruct = template_email.objects.all()

    return render(request, 'template_email.html', {'estruct':estruct, 'year':year, 'destino_email':destino_email})



def read_email_addresses_from_csv(request):
    email_addresses = []
    correos = []

    file_path = '/home/tvacation/thatvacation/csv/subscribed_members_export_8e03086e36.csv'

    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                for cell in row:
                    email = cell.strip()
                    if email and '@' in email:
                        email_addresses.append(email)
                        correos.append(email)
    except Exception as e:
        email_addresses = []

    return render(request, 'correos.html', {'correos': correos})






