# Generated by Django 5.0.7 on 2024-10-18 15:32

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cabin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ship_code', models.CharField(blank=True, max_length=100, null=True)),
                ('cabin_number', models.CharField(blank=True, max_length=10, null=True)),
                ('ship', models.CharField(blank=True, max_length=100, null=True)),
                ('category', models.CharField(blank=True, max_length=10, null=True)),
                ('min_occupancy', models.CharField(blank=True, max_length=3, null=True)),
                ('max_occupancy', models.CharField(blank=True, max_length=3, null=True)),
                ('physically_challenged', models.CharField(blank=True, max_length=3, null=True)),
                ('deck_code', models.CharField(blank=True, max_length=10, null=True)),
                ('deck_desc', models.CharField(blank=True, max_length=100, null=True)),
                ('start_date_validation', models.CharField(blank=True, max_length=10, null=True)),
                ('end_date_validation', models.CharField(blank=True, max_length=10, null=True)),
                ('obs_view', models.CharField(blank=True, max_length=3, null=True)),
                ('bed_arrangement', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='cabinDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ship_cd', models.CharField(db_index=True, max_length=10)),
                ('ship_name', models.CharField(db_index=True, max_length=30)),
                ('cabin_number', models.CharField(max_length=8)),
                ('category_code', models.CharField(db_index=True, max_length=5)),
                ('category_desc', models.CharField(max_length=200)),
                ('min_occupancy', models.IntegerField()),
                ('max_occupancy', models.IntegerField()),
                ('physically_challenged', models.CharField(max_length=10)),
                ('deck_code', models.CharField(max_length=10)),
                ('deck_desc', models.CharField(max_length=200)),
                ('start_date_validation', models.DateField(null=True)),
                ('end_date_validation', models.DateField(null=True)),
                ('obs_view', models.CharField(max_length=20)),
                ('bed_arrmnt', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Cancelations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_note', models.CharField(blank=True, max_length=500, null=True)),
                ('booking_no', models.CharField(blank=True, max_length=10, null=True)),
                ('booking_status', models.CharField(blank=True, max_length=30, null=True)),
                ('total_payments_received', models.CharField(blank=True, max_length=30, null=True)),
                ('gross_balance_due', models.CharField(blank=True, max_length=30, null=True)),
                ('net_balance_due', models.CharField(blank=True, max_length=30, null=True)),
                ('cancelated_at', models.DateTimeField(auto_now_add=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=101)),
                ('codigo', models.CharField(db_index=True, max_length=202)),
                ('fare_cd', models.CharField(db_index=True, max_length=20)),
                ('categoria', models.CharField(db_index=True, max_length=100)),
                ('apply_type', models.CharField(max_length=1)),
                ('apply_method', models.CharField(max_length=1)),
                ('apply_pax', models.CharField(max_length=10)),
                ('price_i', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_j', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_c', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_a', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_s', models.DecimalField(decimal_places=2, max_digits=10)),
                ('descripcion', models.CharField(max_length=200)),
                ('descripcion_larga', models.CharField(max_length=10000)),
                ('package_code', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='compania',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Cruise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cruiseID', models.CharField(db_index=True, max_length=50)),
                ('shipCd', models.CharField(db_index=True, max_length=10)),
                ('sailingPort', models.CharField(db_index=True, max_length=10)),
                ('terminationPort', models.CharField(max_length=10)),
                ('shipName', models.CharField(db_index=True, max_length=100)),
                ('sailingDate', models.DateField(db_index=True, null=True)),
                ('nights', models.PositiveSmallIntegerField(null=True)),
                ('itinCd', models.CharField(db_index=True, max_length=10)),
                ('itinDesc', models.TextField(db_index=True)),
                ('fareCode', models.CharField(db_index=True, max_length=20)),
                ('category', models.CharField(db_index=True, max_length=10)),
                ('fareDesc', models.CharField(db_index=True, max_length=100)),
                ('items', models.TextField(db_index=True, null=True)),
                ('priceType', models.CharField(max_length=10)),
                ('oneAdult', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('threeAdult', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('fourAdult', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult1Ch', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult2Ch', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('oneAdult1Ch', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('oneAdult1JrCh', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult1JrCh', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult1Ch1JrCh', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('twoAdult2JrCh', models.DecimalField(db_index=True, decimal_places=2, max_digits=10, null=True)),
                ('ncfA', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ncfC', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ncfJ', models.DecimalField(decimal_places=2, max_digits=10)),
                ('gftA', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('gftC', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('embkTime', models.CharField(max_length=10)),
                ('disEmbkTime', models.CharField(max_length=10)),
                ('cruiseOnly', models.CharField(max_length=10)),
                ('nowAvailable', models.CharField(max_length=10)),
                ('clubDiscount', models.CharField(max_length=10)),
                ('flightStatus', models.CharField(max_length=10)),
                ('flightPriceType', models.CharField(max_length=10)),
                ('fareStartDate', models.DateField()),
                ('fareStartTime', models.CharField(blank=True, max_length=10, null=True)),
                ('fareEndDate', models.DateField()),
                ('fareEndTime', models.CharField(max_length=10)),
                ('optionExpiresDate', models.DateField(null=True)),
                ('lmtOrgApt', models.CharField(max_length=100, null=True)),
                ('defaultPorts', models.CharField(max_length=10, null=True)),
                ('irCoef', models.CharField(max_length=10, null=True)),
                ('ppdA', models.CharField(max_length=10)),
                ('ppdJc', models.CharField(max_length=10)),
                ('ppdPriceType', models.CharField(max_length=10)),
                ('ppdPriceBasis', models.CharField(max_length=10)),
                ('ppdApplyAs', models.CharField(max_length=10)),
                ('serviceChargeCode', models.CharField(max_length=20)),
                ('serviceChargeSenior', models.CharField(max_length=20)),
                ('serviceChargeAdult', models.CharField(max_length=20)),
                ('serviceChargeChild', models.CharField(max_length=20)),
                ('serviceChargeJunior', models.CharField(max_length=20)),
                ('serviceChargeInfant', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CruiseDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax_type_cd', models.CharField(max_length=255)),
                ('pax_type_desc', models.CharField(max_length=255)),
                ('club_card', models.CharField(blank=True, max_length=255, null=True)),
                ('disc_cd', models.CharField(max_length=255)),
                ('disc_desc', models.CharField(max_length=255)),
                ('disc_class', models.CharField(max_length=1024)),
                ('cruise_limit', models.CharField(max_length=255)),
                ('cruise_id', models.CharField(max_length=255)),
                ('disc_rate_type', models.CharField(max_length=255)),
                ('disc_rate_amt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invtd', models.CharField(blank=True, max_length=255, null=True)),
                ('min_num_a', models.IntegerField(blank=True, null=True)),
                ('max_num_a', models.IntegerField(blank=True, null=True)),
                ('oper_a', models.CharField(blank=True, max_length=255, null=True)),
                ('age_a', models.CharField(blank=True, max_length=255, null=True)),
                ('min_num_c', models.IntegerField(blank=True, null=True)),
                ('max_num_c', models.IntegerField(blank=True, null=True)),
                ('oper_c', models.CharField(blank=True, max_length=255, null=True)),
                ('age_c', models.CharField(blank=True, max_length=255, null=True)),
                ('disc_pos_a', models.CharField(blank=True, max_length=255, null=True)),
                ('disc_pos_c', models.CharField(blank=True, max_length=255, null=True)),
                ('combl', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'Pax Type',
                'verbose_name_plural': 'Pax Type',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=150)),
                ('phone', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Employed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=70, null=True)),
                ('last_name', models.CharField(blank=True, max_length=70, null=True)),
                ('charge', models.CharField(blank=True, max_length=100, null=True)),
                ('image', models.ImageField(blank=True, default='default.webp', upload_to='profile_employed/')),
                ('resume', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type_code', models.CharField(db_index=True, max_length=255)),
                ('item_code', models.CharField(db_index=True, max_length=255)),
                ('fare_code', models.CharField(db_index=True, max_length=255)),
                ('category', models.CharField(db_index=True, max_length=255)),
                ('price_type', models.CharField(blank=True, max_length=255, null=True)),
                ('price_basis', models.CharField(blank=True, max_length=255, null=True)),
                ('pax_applicability', models.CharField(blank=True, max_length=255, null=True)),
                ('price_infant', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price_jr_child', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price_child', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price_adult', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price_senior', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('item_description', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('item_description_long', models.CharField(blank=True, max_length=3500, null=True)),
                ('service_type', models.CharField(blank=True, max_length=255, null=True)),
                ('service_type_desc', models.CharField(blank=True, max_length=255, null=True)),
                ('package_code', models.CharField(blank=True, max_length=255, null=True)),
                ('loc_cd', models.CharField(blank=True, max_length=255, null=True)),
                ('port_cd', models.CharField(blank=True, max_length=255, null=True)),
                ('start_dt', models.DateField(blank=True, null=True)),
                ('end_dt', models.DateField(blank=True, null=True)),
                ('ship_cd', models.CharField(blank=True, max_length=255, null=True)),
                ('inventoried', models.CharField(blank=True, max_length=255, null=True)),
                ('apply_to', models.CharField(blank=True, default='default_value', max_length=255, null=True)),
                ('reg_cd', models.CharField(blank=True, default='default_reg_cd', max_length=255, null=True)),
                ('pax_type', models.CharField(blank=True, default='default_pax_type', max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Itinerary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cruise_id', models.CharField(db_index=True, max_length=20)),
                ('departure_port', models.CharField(db_index=True, max_length=50)),
                ('departure_port_name', models.CharField(max_length=50)),
                ('departure_date', models.DateField()),
                ('departure_day', models.IntegerField()),
                ('departure_weekday', models.CharField(max_length=20)),
                ('departure_time', models.CharField(max_length=10)),
                ('arrival_port', models.CharField(max_length=50)),
                ('arrival_port_name', models.CharField(max_length=50)),
                ('arrival_date', models.DateField()),
                ('arrival_day', models.IntegerField()),
                ('arrival_weekday', models.CharField(max_length=20)),
                ('arrival_time', models.CharField(max_length=10)),
                ('itinerary_cd', models.CharField(max_length=10)),
                ('area_destination', models.CharField(max_length=50)),
                ('region_cd', models.CharField(max_length=10)),
                ('comm_area', models.CharField(max_length=10)),
                ('departure_hour', models.TimeField(blank=True, null=True)),
                ('arrival_hour', models.TimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='paqueteoferta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Destino',
                'verbose_name_plural': 'Destinos',
            },
        ),
        migrations.CreateModel(
            name='prestaciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region_code', models.CharField(max_length=50, unique=True)),
                ('region_description', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
            },
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('agency', models.CharField(max_length=70, null=True)),
                ('phone', models.CharField(max_length=15)),
                ('pais', models.CharField(max_length=150)),
                ('direccion', models.CharField(max_length=150)),
                ('estado', models.CharField(max_length=150)),
                ('iata_clia', models.CharField(blank=True, max_length=15, null=True)),
                ('role', models.CharField(blank=True, choices=[('Select option', 'Select option'), ('Manage a travel agency', 'Manage a Travel Agency'), ('Work in a Travel agency', 'Work in a Travel Agency'), ('Own a home-based agency ', 'Own a home-based agency'), ('Work from home for agency', 'Work form home for agency'), ('Work in a Group/Network HQ', 'Work in a Group/Network HQ'), ('Other', 'Other')], max_length=50, null=True)),
                ('zipcode', models.IntegerField(null=True)),
                ('profile_picture', models.ImageField(blank=True, default='default.webp', upload_to='profile_pics/')),
                ('aprobacion', models.BooleanField(default=False)),
                ('terminos_condiciones', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='customuser_set', related_query_name='user', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_set', related_query_name='user', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_number', models.CharField(default='TEMP-0000', max_length=20, unique=True)),
                ('email', models.CharField(blank=True, max_length=40)),
                ('first_name', models.CharField(blank=True, max_length=20)),
                ('last_name', models.CharField(blank=True, max_length=20)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('ship', models.CharField(blank=True, max_length=100, null=True)),
                ('departure_day', models.CharField(blank=True, max_length=20)),
                ('unique_id', models.BigIntegerField(default=1000, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_payment_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('card_address', models.CharField(blank=True, max_length=300)),
                ('zip_code', models.IntegerField(default=0)),
                ('last_four_digit_card', models.CharField(blank=True, max_length=4)),
                ('type_card', models.CharField(blank=True, max_length=20)),
                ('city', models.CharField(blank=True, max_length=20)),
                ('country', models.CharField(blank=True, max_length=20)),
                ('state', models.CharField(blank=True, max_length=20)),
                ('total_to_pay', models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=10)),
                ('total_paid', models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=10)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), editable=False, max_digits=10)),
                ('dining', models.CharField(blank=True, max_length=25, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Booking Invoice',
                'verbose_name_plural': 'Booking Invoices',
            },
        ),
        migrations.CreateModel(
            name='comentarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=100)),
                ('review', models.TextField(blank=True, max_length=500)),
                ('ip', models.CharField(blank=True, max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CruiseSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_date', models.DateField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('sailingPort', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cruise_searches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booking_context', models.TextField()),
                ('passenger_data_json', models.TextField()),
                ('xml_data', models.TextField()),
                ('response_content', models.TextField(blank=True, null=True)),
                ('cruise', models.CharField(max_length=100, null=True)),
                ('cabin_number', models.CharField(max_length=100, null=True)),
                ('itemtype_list', models.TextField()),
                ('itemcode_list', models.TextField()),
                ('packagecode_list', models.TextField()),
                ('category_list', models.TextField()),
                ('booking_no', models.CharField(max_length=100)),
                ('total', models.CharField(max_length=100, null=True)),
                ('desembarkation_port', models.CharField(max_length=100, null=True)),
                ('embarkation_port', models.CharField(max_length=100, null=True)),
                ('total_general', models.CharField(max_length=100, null=True)),
                ('crucero', models.CharField(max_length=100, null=True)),
                ('metodo_pago', models.CharField(max_length=100, null=True)),
                ('moneda', models.CharField(max_length=100, null=True)),
                ('fecha_salida', models.CharField(max_length=100, null=True)),
                ('fecha_regreso', models.CharField(max_length=100, null=True)),
                ('categoria', models.CharField(max_length=100, null=True)),
                ('lock_id', models.CharField(max_length=100, null=True)),
                ('total_travelers', models.CharField(max_length=100, null=True)),
                ('price_variable', models.CharField(max_length=100, null=True)),
                ('precio', models.CharField(max_length=100, null=True)),
                ('charge_details', models.JSONField()),
                ('booking_charges', models.JSONField()),
                ('deposit_amount_due', models.CharField(max_length=100, null=True)),
                ('final_payment_date', models.CharField(max_length=100, null=True)),
                ('deposit_due_date', models.CharField(max_length=100, null=True)),
                ('total_payments_received', models.CharField(max_length=100, null=True)),
                ('debug_info', models.JSONField()),
                ('one_pax', models.CharField(max_length=100, null=True)),
                ('two_pax', models.CharField(max_length=100, null=True)),
                ('three_pax', models.CharField(max_length=100, null=True)),
                ('four_pax', models.CharField(max_length=100, null=True)),
                ('crucero_fields', models.TextField(blank=True, null=True)),
                ('cabin_categories', models.JSONField()),
                ('items_por_categoria', models.JSONField()),
                ('return_date', models.CharField(max_length=100, null=True)),
                ('charges', models.JSONField()),
                ('current_datetime', models.DateTimeField(auto_now_add=True)),
                ('passenger_data', models.JSONField()),
                ('additional_charges_sum', models.CharField(max_length=100, null=True)),
                ('last_four_digits_card', models.CharField(max_length=4, null=True)),
                ('desglose_passenger_data', models.TextField(blank=True, null=True)),
                ('comission', models.CharField(blank=True, max_length=10, null=True)),
                ('comission_agent', models.CharField(blank=True, max_length=10, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port_code', models.CharField(max_length=50, unique=True)),
                ('port_name', models.CharField(max_length=150)),
                ('country_code', models.CharField(blank=True, max_length=50)),
                ('country_name', models.CharField(blank=True, max_length=100)),
                ('destination', models.ManyToManyField(blank=True, related_name='ports', to='reservas.paqueteoferta')),
            ],
            options={
                'verbose_name': 'Port',
                'verbose_name_plural': 'Ports',
            },
        ),
        migrations.CreateModel(
            name='destino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('fecha_partida', models.DateField()),
                ('fecha_regreso', models.DateField()),
                ('imagen', models.ImageField(upload_to='destinos/')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=8)),
                ('duracion', models.IntegerField()),
                ('itinerario', models.TextField()),
                ('incluye_bebidas', models.BooleanField(default=False)),
                ('incluye_wifi', models.BooleanField(default=False)),
                ('companias', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.compania')),
                ('paquete_oferta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservas.paqueteoferta', verbose_name='Destinos')),
                ('prestaciones_incluidas', models.ManyToManyField(blank=True, to='reservas.prestaciones')),
            ],
            options={
                'verbose_name': 'Paquete Oferta',
                'verbose_name_plural': 'Paquete Ofertas',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_code', models.CharField(max_length=50)),
                ('city_name', models.CharField(max_length=100)),
                ('country_code', models.CharField(blank=True, max_length=50)),
                ('country_name', models.CharField(blank=True, max_length=100)),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='reservas.state')),
            ],
        ),
    ]
