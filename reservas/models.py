from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from datetime import datetime
from django.utils import timezone
import random
from django.utils.crypto import get_random_string



class State(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} - {self.name}"




class City(models.Model):
    city_code = models.CharField(max_length=50)
    city_name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities', null=True)
    country_code = models.CharField(max_length=50, blank=True)
    country_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.city_name


class paqueteoferta(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Destinos'




class Port(models.Model):
    port_code = models.CharField(max_length=50, unique=True)
    port_name = models.CharField(max_length=150)
    country_code = models.CharField(max_length=50, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    destination = models.ManyToManyField(paqueteoferta, related_name="ports", blank=True)

    def __str__(self):
        return f"{self.port_name}"

    class Meta:
        verbose_name = 'Port'
        verbose_name_plural = 'Ports'


class Region(models.Model):
    region_code = models.CharField(max_length=50, unique=True)
    region_description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.region_code} - {self.region_description}"

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'


class CustomUser(AbstractUser):
    CHOICES1 = [
        ('Select option','Select option'),
        ('Manage a travel agency', 'Manage a Travel Agency'),
        ('Work in a Travel agency', 'Work in a Travel Agency'),
        ('Own a home-based agency ', 'Own a home-based agency'),
        ('Work from home for agency', 'Work form home for agency'),
        ('Work in a Group/Network HQ', 'Work in a Group/Network HQ'),
        ('Other','Other')
    ]
    agency = models.CharField(max_length=70, blank=False, null=True)
    phone = models.CharField(max_length=15, blank=False, null=False)
    pais = models.CharField(max_length=150, blank=False, null=False)
    direccion = models.CharField(max_length=150, blank=False, null=False)
    estado = models.CharField(max_length=150, blank=False, null=False)
    iata_clia = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=50, choices=CHOICES1, blank=True, null=True)
    zipcode = models.IntegerField(blank=False, null=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='customuser_set', related_query_name='user')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.webp', blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='customuser_set', related_query_name='user')
    aprobacion = models.BooleanField(default=False)
    terminos_condiciones = models.BooleanField(default = False)







class comentarios(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    ip = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

from decimal import Decimal


class Booking(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,
        blank=True
    )
    booking_number = models.CharField(max_length=20, unique=True, default='TEMP-0000')
    email = models.CharField(max_length=40, blank=True)
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ship = models.CharField(max_length=100, blank=True, null=True)
    departure_day = models.CharField(max_length=20, blank=True)
    unique_id = models.BigIntegerField(unique=True, default=1000)
    created_at = models.DateTimeField(default=timezone.now)
    last_payment_date = models.DateTimeField(default=timezone.now)
    card_address = models.CharField(max_length=300, blank=True)
    zip_code = models.IntegerField(default=0)
    last_four_digit_card = models.CharField(max_length=4, blank=True)
    type_card = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    total_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    dining = models.CharField(max_length=25, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not isinstance(self.total_to_pay, Decimal):
            self.total_to_pay = Decimal(self.total_to_pay)
        if not isinstance(self.total_paid, Decimal):
            self.total_paid = Decimal(self.total_paid)

        # Calcular el balance
        self.balance = self.total_to_pay - self.total_paid
        super().save(*args, **kwargs)

    def _generate_unique_id(self):
        unique_id = random.randint(1000, 999999999999)
        while Booking.objects.filter(unique_id=unique_id).exists():
            unique_id = random.randint(1000, 999999999999)
        return unique_id

    def __str__(self):
        return f'{self.booking_number} - {self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Booking Invoice'
        verbose_name_plural = 'Booking Invoices'






class CruiseSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cruise_searches',
    )
    search_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    end_date = models.DateField()
    sailingPort = models.CharField(max_length=100)





class compania(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre





class destino(models.Model):
    companias = models.ForeignKey(compania, on_delete=models.CASCADE)
    paquete_oferta = models.ForeignKey(paqueteoferta, on_delete=models.CASCADE, verbose_name = 'Destinos')
    nombre = models.CharField(max_length=100)
    fecha_partida = models.DateField()
    fecha_regreso = models.DateField()
    imagen = models.ImageField(upload_to='destinos/')
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion = models.IntegerField()  # Duración en días
    itinerario = models.TextField()
    incluye_bebidas = models.BooleanField(default=False)
    incluye_wifi = models.BooleanField(default=False)
    prestaciones_incluidas = models.ManyToManyField('prestaciones', blank=True)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'Paquete Oferta'
        verbose_name_plural = 'Paquete Ofertas'

class prestaciones(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Cruise(models.Model):
    cruiseID = models.CharField(max_length=50, db_index=True)
    shipCd = models.CharField(max_length=10, db_index=True)
    sailingPort = models.CharField(max_length=10, db_index=True)
    terminationPort = models.CharField(max_length=10)
    shipName = models.CharField(max_length=100, db_index=True)
    sailingDate = models.DateField(null=True, db_index=True)
    nights = models.PositiveSmallIntegerField(null=True)
    itinCd = models.CharField(max_length=10, db_index=True)
    itinDesc = models.TextField(db_index=True)
    fareCode = models.CharField(max_length=20, db_index=True)
    category = models.CharField(max_length=10, db_index=True)
    fareDesc = models.CharField(max_length=100, db_index=True)
    items = models.TextField(null=True, db_index=True)
    priceType = models.CharField(max_length=10)
    oneAdult = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    threeAdult = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    fourAdult = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult1Ch = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult2Ch = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    oneAdult1Ch = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    oneAdult1JrCh = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult1JrCh = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult1Ch1JrCh = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    twoAdult2JrCh = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    ncfA = models.DecimalField(max_digits=10, decimal_places=2)
    ncfC = models.DecimalField(max_digits=10, decimal_places=2)
    ncfJ = models.DecimalField(max_digits=10, decimal_places=2)
    gftA = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    gftC = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    embkTime = models.CharField(max_length=10)
    disEmbkTime = models.CharField(max_length=10)
    cruiseOnly = models.CharField(max_length=10)
    nowAvailable = models.CharField(max_length=10)
    clubDiscount = models.CharField(max_length=10)
    flightStatus = models.CharField(max_length=10)
    flightPriceType = models.CharField(max_length=10)
    fareStartDate = models.DateField()
    fareStartTime = models.CharField(max_length=10, null=True, blank=True)
    fareEndDate = models.DateField()
    fareEndTime = models.CharField(max_length=10)
    optionExpiresDate = models.DateField(null=True)
    lmtOrgApt = models.CharField(max_length=100, null=True)
    defaultPorts = models.CharField(max_length=10, null=True)
    irCoef = models.CharField(max_length=10, null=True)
    ppdA = models.CharField(max_length=10)
    ppdJc = models.CharField(max_length=10)
    ppdPriceType = models.CharField(max_length=10)
    ppdPriceBasis = models.CharField(max_length=10)
    ppdApplyAs = models.CharField(max_length=10)
    serviceChargeCode = models.CharField(max_length=20)
    serviceChargeSenior = models.CharField(max_length=20)
    serviceChargeAdult = models.CharField(max_length=20)
    serviceChargeChild = models.CharField(max_length=20)
    serviceChargeJunior = models.CharField(max_length=20)
    serviceChargeInfant = models.CharField(max_length=20)

    def __str__(self):
        return self.cruiseID





class Cabin(models.Model):
    ship_code = models.CharField(max_length=100, null=True, blank=True)
    cabin_number = models.CharField(max_length=10, null=True, blank=True)
    ship = models.CharField(max_length = 100, null=True, blank=True)
    category = models.CharField(max_length = 10, null=True, blank=True)
    min_occupancy = models.CharField(max_length=3, null=True, blank=True)
    max_occupancy = models.CharField(max_length=3, null=True, blank=True)
    physically_challenged = models.CharField(max_length=3, null=True, blank=True)
    deck_code = models.CharField(max_length=10, null=True, blank=True)
    deck_desc = models.CharField(max_length=100, null=True, blank=True)
    start_date_validation = models.CharField(max_length=10, null=True, blank=True)
    end_date_validation = models.CharField(max_length=10, null=True, blank=True)
    obs_view = models.CharField(max_length=3, null=True, blank=True)
    bed_arrangement = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"{self.cabin_number} on {self.ship}"




class Categories(models.Model):
    tipo = models.CharField(max_length=101)
    codigo = models.CharField(max_length=202, db_index=True)
    fare_cd = models.CharField(max_length=20, db_index=True )
    categoria = models.CharField(max_length=100, db_index=True)
    apply_type = models.CharField(max_length=1)
    apply_method = models.CharField(max_length=1)
    apply_pax = models.CharField(max_length=10)
    price_i = models.DecimalField(max_digits=10, decimal_places=2)
    price_j = models.DecimalField(max_digits=10, decimal_places=2)
    price_c = models.DecimalField(max_digits=10, decimal_places=2)
    price_a = models.DecimalField(max_digits=10, decimal_places=2)
    price_s = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=200)
    descripcion_larga = models.CharField(max_length=10000)
    package_code = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.tipo} - {self.codigo} - {self.fare_cd}"



import datetime

class cabinDetail(models.Model):
    ship_cd = models.CharField(max_length=10, db_index=True)
    ship_name = models.CharField(max_length=30, db_index=True)
    cabin_number = models.CharField(max_length=8)
    category_code = models.CharField(max_length=5, db_index=True)
    category_desc = models.CharField(max_length=200)
    min_occupancy = models.IntegerField()
    max_occupancy = models.IntegerField()
    physically_challenged = models.CharField(max_length=10)
    deck_code = models.CharField(max_length=10)
    deck_desc = models.CharField(max_length=200)
    start_date_validation = models.DateField(null=True)
    end_date_validation = models.DateField(null=True)
    obs_view = models.CharField(max_length=20)
    bed_arrmnt = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.ship_cd} - {self.ship_name} - {self.cabin_number}"



class Item(models.Model):
    item_type_code = models.CharField(max_length=255, db_index=True)
    item_code = models.CharField(max_length=255, db_index=True)
    fare_code = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=255, db_index=True)
    price_type = models.CharField(max_length=255, null=True, blank=True)
    price_basis = models.CharField(max_length=255, null=True, blank=True)
    pax_applicability = models.CharField(max_length=255, null=True, blank=True)
    price_infant = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_jr_child = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_child = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_adult = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price_senior = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    item_description = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    item_description_long = models.CharField(max_length=3500, null=True, blank=True)
    service_type = models.CharField(max_length=255, null=True, blank=True)
    service_type_desc = models.CharField(max_length=255, null=True, blank=True)
    package_code = models.CharField(max_length=255, null=True, blank=True)
    loc_cd = models.CharField(max_length=255, null=True, blank=True)
    port_cd = models.CharField(max_length=255, null=True, blank=True)
    start_dt = models.DateField(null=True, blank=True)
    end_dt = models.DateField(null=True, blank=True)
    ship_cd = models.CharField(max_length=255, null=True, blank=True)
    inventoried = models.CharField(max_length=255, null=True, blank=True)
    apply_to = models.CharField(max_length=255, default="default_value", null=True, blank=True)
    reg_cd = models.CharField(max_length=255, default="default_reg_cd", null=True, blank=True)
    pax_type = models.CharField(max_length=255, default="default_pax_type", null=True, blank=True)
    def __str__(self):
        return self.item_description




class Itinerary(models.Model):
    cruise_id = models.CharField(max_length=20, db_index=True)
    departure_port = models.CharField(max_length=50, db_index=True)
    departure_port_name = models.CharField(max_length=50)
    departure_date = models.DateField()
    departure_day = models.IntegerField()
    departure_weekday = models.CharField(max_length=20)
    departure_time = models.CharField(max_length=10)
    arrival_port = models.CharField(max_length=50)
    arrival_port_name = models.CharField(max_length=50)
    arrival_date = models.DateField()
    arrival_day = models.IntegerField()
    arrival_weekday = models.CharField(max_length=20)
    arrival_time = models.CharField(max_length=10)
    itinerary_cd = models.CharField(max_length=10)
    area_destination = models.CharField(max_length=50)
    region_cd = models.CharField(max_length=10)
    comm_area = models.CharField(max_length=10)
    departure_hour = models.TimeField(null=True, blank=True)
    arrival_hour = models.TimeField(null=True, blank = True)


    def save(self, *args, **kwargs):
        if self.departure_time:
            try:
                hour, minute = map(int, self.departure_time.split(':'))
                self.departure_hour = datetime.time(hour=hour, minute=minute)
            except ValueError:
                pass

        if self.arrival_time:
            try:
                hour, minute = map(int, self.arrival_time.split(':'))
                self.arrival_hour = datetime.time(hour=hour, minute=minute)
            except ValueError:
                pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cruise_id} - {self.departure_port} to {self.arrival_port} ({self.departure_date} to {self.arrival_date})"





class CruiseDiscount(models.Model):
    pax_type_cd = models.CharField(max_length=255)
    pax_type_desc = models.CharField(max_length=255)
    club_card = models.CharField(max_length=255, blank=True, null=True)
    disc_cd = models.CharField(max_length=255)
    disc_desc = models.CharField(max_length=255)
    disc_class = models.CharField(max_length=1024)
    cruise_limit = models.CharField(max_length=255)
    cruise_id = models.CharField(max_length=255)
    disc_rate_type = models.CharField(max_length=255)
    disc_rate_amt = models.DecimalField(max_digits=10, decimal_places=2)
    invtd = models.CharField(max_length=255, blank=True, null=True)
    min_num_a = models.IntegerField(null=True, blank=True)
    max_num_a = models.IntegerField(null=True, blank=True)
    oper_a = models.CharField(max_length=255, blank=True, null=True)
    age_a = models.CharField(max_length=255, blank=True, null=True)
    min_num_c = models.IntegerField(null=True, blank=True)
    max_num_c = models.IntegerField(null=True, blank=True)
    oper_c = models.CharField(max_length=255, blank=True, null=True)
    age_c = models.CharField(max_length=255, blank=True, null=True)
    disc_pos_a = models.CharField(max_length=255, blank=True, null=True)
    disc_pos_c = models.CharField(max_length=255, blank=True, null=True)
    combl = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.pax_type_desc

    class Meta:
        verbose_name = 'Pax Type'
        verbose_name_plural = 'Pax Type'



class Customer(models.Model):
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=150, null=False)
    phone = models.CharField(max_length=15)








class InvoiceCustomer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    booking_context = models.TextField()
    passenger_data_json = models.TextField()
    xml_data = models.TextField()
    response_content = models.TextField(null=True, blank=True)
    cruise = models.CharField(max_length=100, null=True)
    cabin_number = models.CharField(max_length=100, null=True)
    itemtype_list = models.TextField()
    itemcode_list = models.TextField()
    packagecode_list = models.TextField()
    category_list = models.TextField()
    booking_no = models.CharField(max_length=100)
    total = models.CharField(max_length=100, null=True)
    desembarkation_port = models.CharField(max_length=100, null=True)
    embarkation_port = models.CharField(max_length=100, null=True)
    total_general = models.CharField(max_length=100, null=True)
    crucero = models.CharField(max_length=100, null=True)
    metodo_pago = models.CharField(max_length=100, null=True)
    moneda = models.CharField(max_length=100, null=True)
    fecha_salida = models.CharField(max_length=100, null=True)
    fecha_regreso = models.CharField(max_length=100, null=True)
    categoria = models.CharField(max_length=100, null=True)
    lock_id = models.CharField(max_length=100, null=True)
    total_travelers = models.CharField(max_length=100, null=True)
    price_variable = models.CharField(max_length=100, null=True)
    precio = models.CharField(max_length=100, null=True)
    charge_details = models.JSONField()
    booking_charges = models.JSONField()
    deposit_amount_due = models.CharField(max_length=100, null=True)
    final_payment_date = models.CharField(max_length=100, null=True)
    deposit_due_date = models.CharField(max_length=100, null=True)
    total_payments_received = models.CharField(max_length=100, null=True)
    debug_info = models.JSONField()
    one_pax = models.CharField(max_length=100, null=True)
    two_pax = models.CharField(max_length=100, null=True)
    three_pax = models.CharField(max_length=100, null=True)
    four_pax = models.CharField(max_length=100, null=True)
    crucero_fields = models.TextField(null=True, blank=True)
    cabin_categories = models.JSONField()
    items_por_categoria = models.JSONField()
    return_date = models.CharField(max_length=100, null=True)
    charges = models.JSONField()
    current_datetime = models.DateTimeField(auto_now_add=True)
    passenger_data = models.JSONField()
    additional_charges_sum = models.CharField(max_length=100, null=True)
    last_four_digits_card = models.CharField(max_length=4, null=True)
    desglose_passenger_data = models.TextField(null=True, blank= True)
    comission = models.CharField(max_length=10, null=True, blank=True)
    comission_agent = models.CharField(max_length=10, null=True, blank=True)


    def __str__(self):
        return f"Invoice for Booking No: {self.booking_no} by {self.user.username}"




class Cancelations(models.Model):
    booking_note = models.CharField(max_length=500, null=True, blank=True)
    booking_no = models.CharField(max_length=10, null=True, blank=True)
    booking_status = models.CharField(max_length=30, null=True, blank=True)
    total_payments_received = models.CharField(max_length=30, null=True, blank=True)
    gross_balance_due = models.CharField(max_length=30, null=True, blank=True)
    net_balance_due = models.CharField(max_length=30, null=True, blank=True)
    cancelated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(null=True, blank=True)





class Employed(models.Model):
    first_name = models.CharField(max_length=70, null=True, blank=True)
    last_name = models.CharField(max_length=70, null=True, blank=True)
    charge = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='profile_employed/', default='default.webp', blank=True)
    resume = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"






