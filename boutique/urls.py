from django.urls import path
from .views import boutique_view
from . import views
from .views import (
    panier_detail, 
    update_quantite_produit, 
    ajouter_au_panier, 
    retirer_du_panier, 
    commande_confirmation_view, 
    mes_commandes_view, 
    annuler_commande_view, 
    update_quantite_produit_session,
    supprimer_du_panier_session
    )

urlpatterns = [
    path('', boutique_view, name='boutique'),  # vue d'accueil de la boutique
    path('panier/count/', views.panier_count, name='panier_count'),
    path('panier/', panier_detail, name='panier'),
    path('panier/dropdown/', views.panier_dropdown, name='panier_dropdown'), 
    path('panier/update/', update_quantite_produit, name='update_quantite_produit'),
    path('panier/ajouter/<int:produit_id>/', ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/retirer/<int:produit_id>/', retirer_du_panier, name='retirer_du_panier'),
    path('panier/supprimer/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('commande/', views.commande_view, name='commande'),
    path('commande/confirmation/<int:commande_id>/', commande_confirmation_view, name='commande_confirmation'),
    path('mes-commandes/', mes_commandes_view, name='mes_commandes'),
    path('commande/<int:commande_id>/annuler/', annuler_commande_view, name='annuler_commande'),
    path('panier/update-session/', update_quantite_produit_session, name='update_quantite_produit_session'),
    path('panier/supprimer/session/', supprimer_du_panier_session, name='supprimer_du_panier_session'),
]
