from django.db import models
from django.conf import settings
from django.utils import timezone 

class Produit(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # 🔁 remplacé
    nombre_ventes = models.PositiveIntegerField(default=0)  # 🔁 ajouté
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    seuil_alerte = models.PositiveIntegerField(default=0, verbose_name="Seuil d’alerte stock")
    
    def en_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.nom

class Panier(models.Model):
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

class ProduitsPanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='produits')
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def sous_total(self):
        return self.produit.prix * self.quantite

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
    
class Commande(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commandes'
    )
    date_commande = models.DateTimeField(default=timezone.now)
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('payée', 'Payée'),
            ('expédiée', 'Expédiée'),
            ('annulée', 'Annulée'),
        ],
        default='en_attente'
    )

    MOYENS_PAIEMENT = [
        ('carte', 'Carte bancaire'),
        ('paypal', 'Compte PayPal'),
    ]

    moyen_paiement = models.CharField(
        max_length=20,
        choices=MOYENS_PAIEMENT,
        default='carte'
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Commande #{self.id} - {self.utilisateur.email}"

    def annuler_commande(self):
        if self.statut == 'annulée':
            return False  # Déjà annulée

        for ligne in self.lignes.all():
            produit = ligne.produit
            produit.stock += ligne.quantite
            produit.save()

        self.statut = 'annulée'
        self.save()
        return True  # Annulation réussie


class LigneCommande(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    produit = models.ForeignKey(
        'Produit',
        on_delete=models.CASCADE
    )
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom} (Commande #{self.commande.id})"

    def get_total_ligne(self):
        if self.quantite is not None and self.prix_unitaire is not None:
            return self.quantite * self.prix_unitaire
        return 0

