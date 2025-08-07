from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Message facultatif...'})
        }
        labels = {
            'message': 'Message à l’éleveuse (optionnel)'
        }
