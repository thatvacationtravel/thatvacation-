from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from reservas.models import comentarios, Cruise, destino, City, paqueteoferta, CustomUser, Port, Region
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.forms import formset_factory
from datetime import date
from datetime import datetime






class CustomCountrySelectWidget(CountrySelectWidget):
    def render_option(self, selected_choices, option_value, option_label):
        return super().render_option(selected_choices, option_value, option_label)




class UCFWithEmail(UserCreationForm):
    username = forms.CharField(label="Username",widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Uername*"}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Full Name*"}))
    agency = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Agency Name"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Email*"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control bg-transparent", "placeholder": "Password*"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control bg-transparent", "placeholder": "Confirm Password*"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Phone*"}))
    estado = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "State*"}))
    direccion = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Adress*"}))
    zipcode = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Zipcode*"}))
    iata_clia = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "IATA/CLIA"}))
    role = forms.ChoiceField(choices=CustomUser.CHOICES1, widget=forms.Select(attrs={"class": "form-control bg-transparent", "placeholder": "Current Occupation"}))
    pais = CountryField().formfield(
        widget=CustomCountrySelectWidget(
            attrs={"class": "form-control bg-transparent", "placeholder": "Select Country"},
        )
    )
    terminos_condiciones = forms.BooleanField(
        required=True,
        label="Acepto los Términos y Condiciones",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "placeholder": "Acept Terms & Conditions"})
    )

    class Meta:
        model = CustomUser
        fields = ["username", "first_name", "agency", "email", "phone", "password1", "password2", "pais", "estado", "direccion", "zipcode", "iata_clia", "role", "terminos_condiciones"]



class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Nombre Completo*"}))
    agency = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Nombre Agencia*"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Telefono*"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Email*"}))
    direccion = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Address*"}))
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'custom-file-upload'})
    )
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')

        if isinstance(profile_picture, (InMemoryUploadedFile, TemporaryUploadedFile)):

            if not profile_picture.content_type.startswith('image'):
                raise ValidationError(_('Solo se permiten archivos de imagen.'))

            if profile_picture.size > 6 * 1024 * 1024:
                raise ValidationError(_('El tamaño máximo permitido para la imagen es 6MB.'))

        return profile_picture

    class Meta:
        model = CustomUser
        fields = ['profile_picture', "agency", "email", "phone", "first_name","direccion"]





class CustomUserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control bg-transparent", "placeholder": "Password"}))


class CommentForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Asunto"}))
    review = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Comentario"}))
    class Meta:
        model = comentarios
        fields = ['subject', 'review']





class HotelSearchForm(forms.Form):
    hotel = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Hotel", "class": "form-control bg-transparent w-10", "autocomplete": "off"}))
    pais = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={"placeholder": "País", "class": "form-control bg-transparent w-10", "autocomplete": "off", "maxlength": "4"})
    )
    pais_cliente = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={"placeholder": "País Cliente", "class": "form-control bg-transparent w-10", "autocomplete": "off", "maxlength": "4"})
    )
    categoria = forms.IntegerField(
        label='Categoria',
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Categoria"})
    )
    fechaentrada = forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.DateInput(attrs={"placeholder": "Desde", "data-target": "#date", "id": "fecha1", "class": "form-control datepicker-input", "data-toggle": "datetimepicker", "autocomplete": "off"}))
    fechasalida = forms.DateField(input_formats=['%d/%m/%Y'],widget=forms.DateInput(attrs={'placeholder': 'Hasta', "data-target": "#date5", "id": "fecha2", "class": "form-control datepicker-input", "data-toggle": "datetimepicker", "autocomplete": "off"}))




class CruiseSearchForm1(forms.Form):
    departure_date = forms.DateField(
        input_formats=['%m/%d/%Y'],
        widget=forms.DateInput(attrs={
            "placeholder": "From",
            "id": "fecha1",
            "class": "form-control datepicker-input",
            "autocomplete": "off"
        })
    )
    departure_end_date = forms.DateField(
        input_formats=['%m/%d/%Y'],
        widget=forms.DateInput(attrs={
            'placeholder': "To",
            "id": "fecha2",
            "class": "form-control datepicker-input",
            "autocomplete": "off"
        })
    )
    adultos = forms.IntegerField(
        label='Adultos +18',
        min_value=1,
        max_value=4,
        widget=forms.NumberInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Adults"})
    )
    ninos = forms.IntegerField(
        label='Menores -17',
        min_value=0,
        max_value=2,
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Children", "id": "id_ninos"})
    )
    destination = forms.ModelChoiceField(
        queryset=paqueteoferta.objects.all(),
        widget=forms.Select(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Destiny"}),
        label="Destiny",
        required=False,
        empty_label="Select destination"
    )
    port = forms.ChoiceField(
        choices=[('', 'Port')],
        widget=forms.Select(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Port", "id": "id_port"}),
        label="Puerto de Salida",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(CruiseSearchForm1, self).__init__(*args, **kwargs)
        self.fields['port'].choices = self.get_port_choices()

    def get_port_choices(self, destination=None):
        if destination:
            ports = Port.objects.filter(destination=destination)
        else:
            ports = Port.objects.all()
        return [('', 'Departure port'), ('Any Port', 'Any Port')] + [(port.port_code, port.port_name) for port in ports]

    def clean(self):
        cleaned_data = super().clean()
        adultos = cleaned_data.get('adultos')
        ninos = cleaned_data.get('ninos', 0)
        destination = cleaned_data.get('destination')
        port_code = cleaned_data.get('port')

        if (adultos + ninos) > 4:
            raise forms.ValidationError('The total number of adults and children cannot exceed four passengers.')

        self.fields['port'].choices = self.get_port_choices(destination)

        if port_code and port_code not in [choice[0] for choice in self.fields['port'].choices]:
            raise forms.ValidationError({'port': f"Select a valid choice. {port_code} is not one of the available choices."})

        return cleaned_data





class PassengerForm(forms.Form):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    country_choices = list(City.objects.order_by('country_name').values_list('country_code', 'country_name').distinct())
    country_choices = sorted(country_choices, key=lambda x: (x[1] != 'United States', x[1]))

    city = forms.ChoiceField(
        choices=country_choices,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial='US',
        label="Citizenship",
        required=False
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control datepicker-input", "placeholder": "Birthdate*", "autocomplete": "off"}),
        label="Birthdate",
        help_text="Must be over 21 years old.",
        input_formats=['%m/%d/%Y'],
        required=False
    )

    telephone_no = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control bg-transparent w-10", "id":"telephone_no_1", "placeholder": ""}),
        required=False
    )
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Email*"}),
        required=False
    )
    gender = forms.ChoiceField(
        label='Gender',
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "Last Name*"}),
        required=False
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control bg-transparent w-10", "placeholder": "First Name*"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.index = kwargs.pop('index', None)
        super().__init__(*args, **kwargs)

        if self.index == 0:
            # Para el primer pasajero: todos los campos son obligatorios
            for field_name in self.fields:
                self.fields[field_name].required = True
        else:
            # Para los demás pasajeros: solo estos campos son obligatorios
            required_fields = ['first_name', 'last_name', 'date_of_birth', 'city', 'gender']
            for field_name in required_fields:
                self.fields[field_name].required = True

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = datetime.today().date()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            if self.index == 0 and age < 21:
                raise ValidationError('You must be at least 21 years old.')
        return dob

    def clean(self):
        cleaned_data = super().clean()

        if self.index == 0:
            # Validar que todos los campos estén presentes para el primer pasajero
            required_fields = [
                'first_name', 'last_name', 'city', 'date_of_birth', 'telephone_no',
                'email', 'gender'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required.')









class DinigForm(forms.Form):
    Dining_CHOICES = [
        ('L', 'Late'),
        ('E', 'Early'),
    ]

    dining_preference = forms.ChoiceField(
        label='Dining Preference',
        choices=Dining_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )


class EmailForm(forms.Form):
    subject = forms.CharField(
        label='Asunto del Correo',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto de email'})
    )
    encabezado = forms.CharField(
        label='Encabezado',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Encabezado de la promocion'})
    )

    video = forms.CharField(
        label='Video',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL Video Promocional'})
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Cuerpo de la promocion'})
    )
    recipients = forms.CharField(
        label='Destinatarios',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 5,
            'placeholder': 'Ingrese los correos electrónicos de los destinatarios, separados por comas'
        })
    )
    image1 = forms.ImageField(
        label='Imagen 1',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image2 = forms.ImageField(
        label='Imagen 2',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image3 = forms.ImageField(
        label='Imagen 3',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image4 = forms.ImageField(
        label='Imagen 4',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image5 = forms.ImageField(
        label='Imagen 5',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )




class DinigForm(forms.Form):
    Dining_CHOICES = [
        ('L', 'Late'),
        ('E', 'Early'),
    ]

    dining_preference = forms.ChoiceField(
        label='Dining Preference',
        choices=Dining_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )


class EmailForm(forms.Form):
    subject = forms.CharField(
        label='Asunto del Correo',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto de email'})
    )
    encabezado = forms.CharField(
        label='Encabezado',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Encabezado de la promocion'})
    )

    video = forms.CharField(
        label='Video',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL Video Promocional'})
    )
    message = forms.CharField(
        label='Mensaje',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Cuerpo de la promocion'})
    )
    recipients = forms.CharField(
        label='Destinatarios',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 5,
            'placeholder': 'Ingrese los correos electrónicos de los destinatarios, separados por comas'
        })
    )
    image1 = forms.ImageField(
        label='Imagen 1',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image2 = forms.ImageField(
        label='Imagen 2',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image3 = forms.ImageField(
        label='Imagen 3',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image4 = forms.ImageField(
        label='Imagen 4',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image5 = forms.ImageField(
        label='Imagen 5',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
