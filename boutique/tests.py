from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from boutique.models import Commande

User = get_user_model()

class CommandeAccessTest(TestCase):
    def setUp(self):
        # Crée deux utilisateurs
        self.user1 = User.objects.create_user(
            username='user1', email='user1@test.local', password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@test.local', password='pass123'
        )

        # Crée une commande pour user1
        self.commande_user1 = Commande.objects.create(
            utilisateur=self.user1,
            moyen_paiement='carte',
            total=100.0
        )

        self.client = Client()

    def test_acces_autorise(self):
        # user1 se connecte
        self.client.force_login(self.user1)

        # Accès à sa propre commande : doit fonctionner
        response = self.client.get(reverse('commande_confirmation', args=[self.commande_user1.id]))
        self.assertEqual(response.status_code, 200)

    def test_acces_non_autorise(self):
        # user2 se connecte
        self.client.force_login(self.user2)

        # Tente d'accéder à la commande de user1 : doit échouer
        response = self.client.get(reverse('commande_confirmation', args=[self.commande_user1.id]))
        self.assertEqual(response.status_code, 404)
