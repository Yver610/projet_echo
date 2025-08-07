from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .utils import get_panier

from .models import Produit, Panier, ProduitsPanier, Commande, LigneCommande

import logging

logger = logging.getLogger('boutique')

def boutique_view(request):
    produits = Produit.objects.all()
    return render(request, 'boutique/boutique.html', {'produits': produits})

def panier_count(request):
    if request.user.is_authenticated:
        try:
            panier = Panier.objects.get(utilisateur=request.user)
            count = sum([p.quantite for p in panier.produits.all()])
        except Panier.DoesNotExist:
            count = 0
    else:
        panier_session = request.session.get('panier', {})
        count = sum(item['quantite'] for item in panier_session.values())

    return JsonResponse({'count': count})

def panier_detail(request):
    return render(request, 'boutique/panier_detail.html')

@require_GET
def panier_dropdown(request):
    produits_data = []
    total = 0

    panier = get_panier(request)

    # ✅ Cas utilisateur connecté
    if request.user.is_authenticated:
        produits = panier.produits.select_related('produit')
        for item in produits:
            sous_total_item = item.sous_total()
            produits_data.append({
                'id': item.produit.id,
                'nom': item.produit.nom,
                'quantite': item.quantite,
                'prix_unitaire': float(item.produit.prix),
                'sous_total': float(sous_total_item),
                'stock': item.produit.stock,
                'image': item.produit.image.url if item.produit.image else None
            })
            total += sous_total_item

    # ✅ Cas utilisateur non connecté (panier session)
    else:
        panier_session = panier  # dict
        from .models import Produit  # import ici car sinon circular import possible

        for produit_id_str, data in panier_session.items():
            try:
                produit = Produit.objects.get(id=int(produit_id_str))
                quantite = data['quantite']
                sous_total_item = quantite * produit.prix

                produits_data.append({
                    'id': produit.id,
                    'nom': produit.nom,
                    'quantite': quantite,
                    'prix_unitaire': float(produit.prix),
                    'sous_total': float(sous_total_item),
                    'stock': produit.stock,
                    'image': produit.image.url if produit.image else None
                })

                total += sous_total_item

            except Produit.DoesNotExist:
                continue

    return JsonResponse({
        'produits': produits_data,
        'total': float(round(total, 2))
    })
    
@csrf_exempt
@require_POST
@login_required
def update_quantite_produit(request):
    produit_id = request.POST.get('produit_id')
    action = request.POST.get('action')  # 'plus' ou 'moins'

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        produit_panier = ProduitsPanier.objects.get(panier=panier, produit_id=produit_id)
        produit = produit_panier.produit

        if not produit.actif:
            return JsonResponse({'status': 'error', 'message': 'Produit désactivé'}, status=400)

        if action == 'plus':
            if produit_panier.quantite + 1 > produit.stock:
                return JsonResponse({'status': 'error', 'message': 'Stock insuffisant'}, status=400)
            produit_panier.quantite += 1

        elif action == 'moins' and produit_panier.quantite > 1:
            produit_panier.quantite -= 1

        produit_panier.save()
        return JsonResponse({'status': 'ok', 'nouvelle_quantite': produit_panier.quantite})

    except (Panier.DoesNotExist, ProduitsPanier.DoesNotExist):
        return JsonResponse({'status': 'error'}, status=404)

@csrf_exempt  # ou à remplacer si tu gères bien le token dans le JS
@require_POST
def update_quantite_produit_session(request):
    produit_id = request.POST.get('produit_id')
    action = request.POST.get('action')

    try:
        produit = Produit.objects.get(id=produit_id)
        if not produit.actif:
            return JsonResponse({'status': 'error', 'message': 'Produit désactivé'}, status=400)

        panier_session = get_panier(request)  # dict
        produit_id_str = str(produit_id)

        if produit_id_str not in panier_session:
            return JsonResponse({'status': 'error', 'message': 'Produit non dans le panier'}, status=404)

        quantite_actuelle = panier_session[produit_id_str]['quantite']

        if action == 'plus':
            if quantite_actuelle + 1 > produit.stock:
                return JsonResponse({'status': 'error', 'message': 'Stock insuffisant'}, status=400)
            panier_session[produit_id_str]['quantite'] += 1

        elif action == 'moins' and quantite_actuelle > 1:
            panier_session[produit_id_str]['quantite'] -= 1

        request.session.modified = True
        return JsonResponse({'status': 'ok', 'nouvelle_quantite': panier_session[produit_id_str]['quantite']})

    except Produit.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Produit introuvable'}, status=404)

@require_POST
def ajouter_au_panier(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)

        if not produit.actif:
            return JsonResponse({'success': False, 'message': 'Ce produit est indisponible.'}, status=400)

        quantite = int(request.POST.get('quantite', 1))
        if quantite < 1:
            return JsonResponse({'success': False, 'message': 'Quantité invalide'}, status=400)

        if not produit.en_stock():
            return JsonResponse({'success': False, 'message': 'Ce produit est en rupture de stock.'}, status=400)

        panier = get_panier(request)

        # ✅ Cas utilisateur connecté : panier BDD
        if request.user.is_authenticated:
            produit_panier, created = ProduitsPanier.objects.get_or_create(panier=panier, produit=produit)

            if created:
                if quantite > produit.stock:
                    return JsonResponse({'success': False, 'message': 'Stock insuffisant.'}, status=400)
                produit_panier.quantite = quantite
            else:
                nouvelle_quantite = produit_panier.quantite + quantite
                if nouvelle_quantite > produit.stock:
                    return JsonResponse({'success': False, 'message': 'Stock insuffisant.'}, status=400)
                produit_panier.quantite = nouvelle_quantite

            produit_panier.save()

        else:
            panier_session = request.session.get('panier', {})
            produit_id_str = str(produit_id)

            # Ajout au panier en session pour un utilisateur anonyme
            # Utiliser le logger plutôt qu'un print afin de ne pas polluer la sortie standard
            logger.debug("Ajout au panier session en cours…")

            if produit_id_str in panier_session:
                nouvelle_quantite = panier_session[produit_id_str]['quantite'] + quantite
                if nouvelle_quantite > produit.stock:
                    return JsonResponse({'success': False, 'message': 'Stock insuffisant'}, status=400)
                panier_session[produit_id_str]['quantite'] = nouvelle_quantite
            else:
                if quantite > produit.stock:
                    return JsonResponse({'success': False, 'message': 'Stock insuffisant'}, status=400)
                panier_session[produit_id_str] = {'quantite': quantite}

            request.session['panier'] = panier_session  # ✅ Réinjecter dans la session
            request.session.modified = True


        return JsonResponse({'success': True})

    except Produit.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produit introuvable'}, status=404)
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Quantité invalide'}, status=400)

@require_GET
@login_required
def retirer_du_panier(request, produit_id):
    try:
        produit = Produit.objects.get(id=produit_id)
        panier = Panier.objects.get(utilisateur=request.user)
        item = ProduitsPanier.objects.get(panier=panier, produit=produit)
        if item.quantite > 1:
            item.quantite -= 1
            item.save()
        else:
            item.delete()
        return JsonResponse({'status': 'ok'})
    except (Produit.DoesNotExist, Panier.DoesNotExist, ProduitsPanier.DoesNotExist):
        return HttpResponseBadRequest('Erreur lors du retrait')
    
@require_POST
@login_required
def supprimer_du_panier(request):
    produit_id = request.POST.get('produit_id')
    if not produit_id:
        return JsonResponse({'status': 'error', 'message': 'ID manquant'})

    try:
        panier = Panier.objects.get(utilisateur=request.user)
        item = ProduitsPanier.objects.get(panier=panier, produit_id=produit_id)
        item.delete()
        return JsonResponse({'status': 'ok'})

    except (Panier.DoesNotExist, ProduitsPanier.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Produit non trouvé'})


@require_POST
@csrf_exempt  # uniquement si pas encore protégé CSRF ailleurs
def supprimer_du_panier_session(request):
    produit_id = request.POST.get('produit_id')

    try:
        panier = get_panier(request)

        if not request.user.is_authenticated:
            produit_id_str = str(produit_id)
            if produit_id_str in panier:
                del panier[produit_id_str]
                request.session.modified = True
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Produit introuvable'}, status=404)

        # Si l’utilisateur est connecté, on ne traite pas ici (vue déjà existante sûrement)
        return JsonResponse({'status': 'error', 'message': 'Utilisateur connecté — mauvaise vue'}, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# La vue `panier_view` n'est plus utilisée.  Le panier est rendu via `panier_detail`.

@login_required
def commande_view(request):
    panier = Panier.objects.filter(utilisateur=request.user).first()
    produits = panier.produits.select_related('produit') if panier else []

    if request.method == 'POST':
        if not panier or not produits:
            logger.warning(f"[POST] Panier vide ou introuvable — utilisateur={request.user}")
            return HttpResponseForbidden("Panier introuvable ou vide.")

        for item in produits:
            if item.panier != panier:
                logger.warning(f"[POST] Accès interdit : utilisateur={request.user} — item ID={item.id}")
                return HttpResponseForbidden("Produit non autorisé.")

            quantite_demandee = int(request.POST.get(f'quantite_{item.id}', item.quantite))
            if quantite_demandee > item.produit.stock:
                logger.info(f"[POST] Stock insuffisant — utilisateur={request.user} — produit={item.produit.nom}")
                messages.error(request, f"Stock insuffisant pour : {item.produit.nom}")
                return redirect('commande')

            if not item.produit.actif:
                logger.warning(f"[POST] Produit inactif — utilisateur={request.user} — produit={item.produit.nom}")
                return HttpResponseForbidden("Produit désactivé.")

        moyen_paiement = request.POST.get('moyen_paiement')
        if not moyen_paiement:
            logger.warning(f"[POST] Moyen de paiement manquant — utilisateur={request.user}")
            return HttpResponseForbidden("Moyen de paiement requis.")

        commande = Commande.objects.create(
            utilisateur=request.user,
            moyen_paiement=moyen_paiement,
        )

        total = 0
        for item in produits:
            prix_unitaire = item.produit.prix
            quantite = item.quantite

            LigneCommande.objects.create(
                commande=commande,
                produit=item.produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire
            )

            item.produit.stock -= quantite
            item.produit.save()

            if item.produit.stock <= item.produit.seuil_alerte:
                logger.warning(
                    f"[STOCK] Stock faible — produit={item.produit.nom} — stock={item.produit.stock}"
                )

            total += prix_unitaire * quantite

        commande.total = total
        commande.save()

        send_mail(
            subject=f"Confirmation de votre commande #{commande.id}",
            message=(
                f"Bonjour {request.user.first_name or request.user.username},\n\n"
                f"Votre commande n°{commande.id} est bien enregistrée.\n"
                f"Montant : {commande.total:.2f} €\n"
                f"Paiement : {commande.get_moyen_paiement_display()}\n\n"
                "Merci pour votre confiance !"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        logger.info(f"[POST] Commande #{commande.id} validée — utilisateur={request.user}")
        panier.produits.all().delete()
        request.session['commande_confirmee'] = True
        return redirect('commande_confirmation', commande_id=commande.id)

    # ✅ Bloc GET bien séparé maintenant
    total = sum(item.quantite * item.produit.prix for item in produits)

    context = {
        'produits': produits,
        'total': total,
    }
    return render(request, 'boutique/commande.html', context)

@login_required
def commande_confirmation_view(request, commande_id):
    commande = Commande.objects.filter(id=commande_id).first()

    if not commande or commande.utilisateur != request.user:
        logger.warning(
            f"[ACCESS] Tentative d'accès non autorisé — utilisateur={request.user} — commande_id={commande_id}"
        )
        raise Http404("Commande introuvable")

    juste_validee = request.session.pop('commande_confirmee', False)

    context = {
        'commande': commande,
        'lignes': commande.lignes.all(),
        'juste_validee': juste_validee,
    }
    return render(request, 'boutique/commande_confirmation.html', context)

@login_required
def mes_commandes_view(request):
    commandes = Commande.objects.filter(utilisateur=request.user).order_by('-date_commande')

    context = {
        'commandes': commandes,
    }
    return render(request, 'boutique/mes_commandes.html', context)

@login_required
def annuler_commande_view(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)

    if commande.statut != 'annulée':
        success = commande.annuler_commande()
        if success:
            messages.success(request, f"Commande #{commande.id} annulée et stock remis à jour.")
        else:
            messages.warning(request, f"Commande #{commande.id} déjà annulée.")
    else:
        messages.warning(request, f"Commande #{commande.id} déjà annulée.")

    return redirect('mes_commandes')  # ou le nom réel de ta vue liste des commandes