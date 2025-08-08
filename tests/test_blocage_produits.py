import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from boutique.models import Produit

@pytest.mark.django_db
def test_ajout_produit_inactif_panier(client):
    # Création d’un produit inactif
    produit = Produit.objects.create(nom="Produit test inactif", prix=10, stock=5, actif=False)

    # Tentative d’ajout au panier via URL
    url = reverse('ajouter_au_panier', args=[produit.id])
    response = client.post(url)

    assert response.status_code == 400
    assert b"Ce produit est indisponible." in response.content

@pytest.mark.django_db
def test_ajout_quantite_superieure_au_stock(client):
    # Création d’un utilisateur
    User = get_user_model()
    user = User.objects.create_user(username='client', password='pass1234')
    client.force_login(user)

    # Création d’un produit avec stock limité
    produit = Produit.objects.create(nom='Test Stock', prix=5.0, stock=2, seuil_alerte=1, actif=True)

    # Tentative d’ajouter plus que le stock
    url = reverse('ajouter_au_panier', args=[produit.id])
    url = reverse('ajouter_au_panier', args=[produit.id])
    response = client.post(url, {'quantite': 5})  # ✅ Envoie en tant que données de formulaire classiques


    assert response.status_code == 400
    assert b"Stock insuffisant" in response.content