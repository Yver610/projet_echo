# tests/test_securite_acces.py

import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
def test_profil_non_connecte(client):
    url = reverse('profil')
    response = client.get(url)
    assert response.status_code == 302  # redirigé vers login
    assert '/connexion/' in response.url

@pytest.mark.django_db
def test_acces_vue_profil_non_authentifie_redirige_login():
    client = Client()
    url = reverse("profil")  # Vérifie bien que c’est le bon nom
    response = client.get(url)

    assert response.status_code == 302  # Redirection attendue
    assert "/login" in response.url or "/connexion" in response.url