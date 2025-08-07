from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    prenom = models.CharField(max_length=150)
    nom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True)
    adresse_postale = models.TextField(blank=True)
    adresse_facturation = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    newsletter = models.BooleanField(default=False)
    civilite = models.CharField(max_length=10, choices=[('M', 'Monsieur'), ('Mme', 'Madame')], blank=True)
    email = models.EmailField(unique=True)
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # obligatoire pour héritage d’AbstractUser

    def __str__(self):
        return self.username
