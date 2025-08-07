from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

CustomUser = get_user_model()

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Adresse email')
    prenom = forms.CharField(required=True, label='Prénom')
    nom = forms.CharField(required=True, label='Nom')
    telephone = forms.CharField(required=False, label='Téléphone')
    adresse_postale = forms.CharField(widget=forms.Textarea, required=False, label='Adresse postale')
    adresse_facturation = forms.CharField(widget=forms.Textarea, required=False, label='Adresse de facturation')
    civilite = forms.ChoiceField(choices=[('M', 'Monsieur'), ('Mme', 'Madame')], required=False, label='Civilité')
    newsletter = forms.BooleanField(required=False, label='S’inscrire à la newsletter')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2',
            'civilite', 'prenom', 'nom', 'telephone',
            'adresse_postale', 'adresse_facturation', 'newsletter'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            else:
                field.widget.attrs.update({'class': 'form-control'})



class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Adresse email"),
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': 'form-control'}),
    )

    from django import forms


class ProfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'email', 'civilite', 'prenom', 'nom',
            'telephone', 'adresse_postale', 'adresse_facturation', 'newsletter'
        ]
        labels = {
            'email': 'Adresse email',
            'civilite': 'Civilité',
            'prenom': 'Prénom',
            'nom': 'Nom',
            'telephone': 'Téléphone',
            'adresse_postale': 'Adresse postale',
            'adresse_facturation': 'Adresse de facturation',
            'newsletter': 'Recevoir la newsletter',
        }
        widgets = {
            'adresse_postale': forms.Textarea(attrs={'rows': 2}),
            'adresse_facturation': forms.Textarea(attrs={'rows': 2}),
        }
