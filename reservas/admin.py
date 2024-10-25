from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from reservas.models import State, comentarios, compania,Itinerary, Employed, Cancelations, Cabin,InvoiceCustomer, CruiseDiscount, Booking, Item, cabinDetail, Categories, destino, paqueteoferta, Port, prestaciones, Cruise, CustomUser, CruiseSearch, Region, City
from django.contrib.auth import get_user_model







class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_number', 'user', 'email', 'first_name', 'last_name',
        'phone', 'ship', 'departure_day', 'unique_id', 'total_to_pay',
        'total_paid', 'balance', 'created_at', 'last_payment_date',
    )
    search_fields = ('booking_number', 'email', 'first_name', 'last_name')
    list_filter = ('created_at', 'ship', 'last_payment_date')

    # Configura los campos que se mostrarán en el formulario de detalle
    fields = (
        'booking_number', 'user', 'email', 'first_name', 'last_name',
        'phone', 'ship', 'departure_day', 'unique_id', 'created_at','last_payment_date', 'card_address', 'zip_code',
        'last_four_digit_card', 'type_card', 'city', 'country', 'state', 'dining'
    )







class CruiseAdmin(admin.ModelAdmin):
    search_fields = ['cruiseID', 'shipName', 'itinDesc', 'fareCode']

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['item_type_code', 'item_code', 'category', 'package_code', 'fare_code']


class ItineraryAdmin(admin.ModelAdmin):
    search_fields = ['cruise_id']



class CategoriesAdmin(admin.ModelAdmin):
    search_fields = ['fare_cd', 'categoria', 'codigo']



class PortAdmin(admin.ModelAdmin):
    search_fields = ['country_name', 'port_code', 'country_code']



class CabinAdmin(admin.ModelAdmin):
    search_fields = ['ship']


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name','agency', 'last_name','direccion', 'aprobacion','terminos_condiciones', 'is_staff')

    list_filter = ('aprobacion', 'is_staff', 'is_superuser')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(username='true')


    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'agency','phone','direccion')}),
        ('Permissions', {'fields': ('aprobacion','terminos_condiciones', 'is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email','agency','phone', 'profile_picture')}),
        ('Permissions', {'fields': ('aprobacion', 'is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
    )







class CancelationsAdmin(admin.ModelAdmin):
    list_display = ('booking_no', 'booking_status', 'total_payments_received', 'gross_balance_due', 'net_balance_due', 'cancelated_at', 'created_at')



InvoiceCustomer
admin.site.register(Cabin, CabinAdmin)
admin.site.register(CruiseDiscount)
admin.site.register(Employed)
admin.site.register(Cancelations, CancelationsAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(cabinDetail)
admin.site.register(State)
admin.site.register(Itinerary, ItineraryAdmin)
admin.site.register(City)
admin.site.register(InvoiceCustomer)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Region)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(CruiseSearch)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(compania)
admin.site.register(Cruise, CruiseAdmin)
admin.site.register(prestaciones)
admin.site.register(paqueteoferta)
admin.site.register(destino)
admin.site.register(comentarios)