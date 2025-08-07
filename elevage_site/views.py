from django.shortcuts import render
from naissances.models import Portee, Chiot
from boutique.models import Produit

def home(request):
    chiots_mis_en_avant = []

    portees = Portee.objects.order_by('date_naissance')

    for portee in portees:
        chiot = portee.chiots.filter(disponible=True).order_by('id').first()
        if chiot:
            chiots_mis_en_avant.append(chiot)
        if len(chiots_mis_en_avant) >= 3:
            break

    produits_populaires = Produit.objects.filter(stock__gt=0).order_by('-nombre_ventes')[:3]  # ✅ déplacé ici

    return render(request, 'home.html', {
        'chiots_mis_en_avant': chiots_mis_en_avant,
        'produits_populaires': produits_populaires,
    })


def a_propos(request):
    return render(request, 'a_propos.html')
