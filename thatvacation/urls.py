from django.contrib import admin
from django.urls import path, include
from reservas.views import (index, pack, donotsale, generate_invoice,endpoint_experience, bookingpro, about, services, register, login_view, logout,
bestdeal, ofertas, politicprivacy,process_payment1,load_ports,contact, detail_employed, experience, cabins, ObtenerCabinasView, process_payment,seleccion_cabinas, buscar_cruceros,
termcondition,cookies_policy, calcular_precio,go_back_view,cancelation, get_states, get_cities,  record_payment, search_bookings, myaccounts, template, error, search_cruises, enviar_correo_promocional, read_email_addresses_from_csv)
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView







urlpatterns = [
    path('admin/', admin.site.urls),
    path('go-back/', go_back_view, name='go_back_view'),
    path('do_not_sale_personal/', donotsale, name='donotsale'),
    path('detail_employed/<int:employed_id>/', detail_employed, name='detail_employed'),
    path('endpoint_experience/<str:crucero_id>/<str:priceVariable>/', endpoint_experience, name='endpoint_experience'),
    path('contact/', contact, name='contact'),
    path('generate-invoice/', generate_invoice, name='generate_invoice'),
    path('get_states/', get_states, name='get_states'),
    path('get_cities/<str:state_name>/', get_cities, name='get_cities'),
    path('', index, name='index'),
    path('ajax/load-ports/', load_ports, name='ajax_load_ports'),
    path('cookies-policy/', cookies_policy, name='cookies_policy'),
    path('calcular_precio/', calcular_precio, name='calcular_precio'),
    path('buscar_cruceros/',buscar_cruceros, name='buscar_cruceros'),
    path('cabinas/<str:crucero_id>/', cabins, name='cabinas'),
    path('experience/<str:crucero_id>/<str:priceVariable>/', experience, name='experience'),
    path('record_payment/<str:booking_no>/', record_payment, name='record_payment'),
    path('template/',template, name='template'),
    path('send_mail/',enviar_correo_promocional, name='send_mail'),
    #path('listado/',read_email_addresses_from_csv, name='read_email_addresses_from_csv'),
    path('politicprivacy/',politicprivacy, name='politicprivacy'),
    path('error/',error, name='error'),
    path('termcondition/',termcondition, name='termcondition'),
    path('seleccioncabinas/<str:cruise_id>/<str:itemcode>/<str:itemtype>/<str:packagecode>', seleccion_cabinas, name='seleccioncabinas'),
    path('bookingpro/<str:cruise_id>/<str:price_variable>/<str:cabin_number>/<str:priceType>/<str:fareCode>/', bookingpro, name='bookingpro'),
    path('search_bookings/', search_bookings, name='search_bookings'),
    path('process_payment/<str:booking_no>/<str:total>', process_payment1, name='process_payment'),
    path('process_payment1/<str:booking_no>/<str:total>', process_payment1, name='process_payment1'),
    path('cancelation/', cancelation, name='cancelation'),
    path('search_cruises/', search_cruises, name='search_cruises'),
    path('myaccounts/', myaccounts, name='myaccounts'),
    path('package/', pack),
    path('about/', about),
    path('service/', services, name='service'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    path('bestdeal/', bestdeal, name='bestdeal'),
    path('ofertas/<int:paquete_id>/<nombre>', ofertas, name='ofertas'),
    path('obtener_cabinas/<str:cruise_id>/<str:categoria>/', ObtenerCabinasView.as_view(), name='obtener_cabinas'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('', include('pwa.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT,)


urlpatterns += [
    path('serviceworker.js', TemplateView.as_view(template_name='serviceworker.js', content_type='application/javascript'), name='serviceworker'),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]