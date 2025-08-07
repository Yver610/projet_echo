from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Commande

@receiver(pre_delete, sender=Commande)
def remettre_stock_si_commande_supprimee(sender, instance, **kwargs):
    print(f"⚠️ Signal pre_delete déclenché pour commande #{instance.id}")

    if instance.statut == 'annulée':
        print("Commande déjà annulée — stock déjà remonté.")
        return

    for ligne in instance.lignes.all():
        produit = ligne.produit
        produit.stock += ligne.quantite
        produit.save()
        print(f"✅ Stock du produit '{produit.nom}' remonté de {ligne.quantite}.")
