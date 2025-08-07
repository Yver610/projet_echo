import logging
from .models import Panier

logger = logging.getLogger(__name__)

def verifier_stock_critique(produit):
    """Déclenche une alerte si le stock du produit est inférieur ou égal au seuil d'alerte."""
    if produit.stock <= produit.seuil_alerte:
        logger.warning(
            f"[STOCK] Stock faible — produit='{produit.nom}' — stock={produit.stock} — seuil={produit.seuil_alerte}"
        )

def get_panier(request):
    if request.user.is_authenticated:
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        return panier
    else:
        # Initialise le panier en session si absent
        if 'panier' not in request.session:
            request.session['panier'] = {}
        return request.session['panier']
