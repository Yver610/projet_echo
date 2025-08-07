from django.shortcuts import render, redirect
from .models import Portee
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .forms import ReservationForm
from .models import Chiot, Reservation
from django.contrib import messages


def page_naissances(request):
    portees = Portee.objects.prefetch_related('chiots').all()
    return render(request, 'naissances/naissances.html', {'portees': portees})


@login_required
def reserver_chiot(request, chiot_id):
    chiot = get_object_or_404(Chiot, id=chiot_id)

    # Vérifie s’il existe déjà une réservation
    reservation_existante = Reservation.objects.filter(
        chiot=chiot,
        utilisateur=request.user
    ).exists()

    if reservation_existante:
        messages.warning(request, "Vous avez déjà réservé ce chiot.")
        return redirect('liste_portees')

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.chiot = chiot
            reservation.utilisateur = request.user
            reservation.save()

            chiot.disponible = False
            chiot.save()
            
            messages.success(request, "Votre demande de réservation a bien été enregistrée.")
            return redirect('liste_portees')
    else:
        form = ReservationForm()

    return render(request, 'naissances/reservation_chiot.html', {
        'chiot': chiot,
        'form': form
    })
