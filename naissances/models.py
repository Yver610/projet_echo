from django.db import models
from django.conf import settings

class Portee(models.Model):
    nom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class Chiot(models.Model):
    portee = models.ForeignKey(Portee, on_delete=models.CASCADE, related_name='chiots')
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='chiots/', blank=True, null=True)

    def __str__(self):
        return self.nom

class Reservation(models.Model):
    chiot = models.ForeignKey(Chiot, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    date_reservation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réservation de {self.chiot.nom} par {self.utilisateur.username}"