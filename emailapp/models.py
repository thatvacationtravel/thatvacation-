from django.db import models


class template_email(models.Model):
    nombre_tmplate = models.CharField(max_length=250)
    imagen1 = models.ImageField(upload_to='destinos/', null=True, blank=True)
    imagen2 = models.ImageField(upload_to='destinos/', null=True, blank=True)
    imagen3 = models.ImageField(upload_to='destinos/', null=True, blank=True)
    imagen4 = models.ImageField(upload_to='destinos/', null=True, blank=True)
    imagen5 = models.ImageField(upload_to='destinos/', null=True, blank=True)
    video = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.nombre_tmplate