from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from django.contrib.auth.decorators import login_required
from boutique.models import Panier, ProduitsPanier, Produit

def inscription_view(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # 🛒 Migration du panier session vers panier utilisateur
            panier_session = request.session.get('panier', {})
            print("PANIER SESSION:", panier_session)
            if panier_session:
                panier_utilisateur = Panier.objects.create(utilisateur=user)
                for produit_id, item_data in panier_session.items():
                    try:
                        quantite = item_data.get('quantite', 1)
                        ProduitsPanier.objects.create(
                            panier=panier_utilisateur,
                            produit_id=produit_id,
                            quantite=quantite
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'ajout du produit {produit_id} au panier : {e}")

                # Supprime le panier de la session
                del request.session['panier']
                request.session.modified = True

            next_url = request.GET.get('next')
            messages.success(request, "Inscription réussie. Vous êtes maintenant connecté.")
            return redirect(next_url or 'home')
    else:
        form = InscriptionForm()

    return render(request, 'comptes/inscription.html', {'form': form})

def connexion_view(request):
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # 'username' = email chez nous
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                # 🔁 Migration panier session → base utilisateur
                panier_session = request.session.get("panier", {})
                if panier_session:
                    panier_utilisateur, _ = Panier.objects.get_or_create(utilisateur=user)

                    for produit_id, item_data in panier_session.items():
                        try:
                            produit = Produit.objects.get(id=produit_id)
                            quantite = item_data.get('quantite', 1)

                            produit_panier, created = ProduitsPanier.objects.get_or_create(
                                panier=panier_utilisateur,
                                produit=produit,
                                defaults={'quantite': quantite}
                            )
                            if not created:
                                produit_panier.quantite += quantite
                                produit_panier.save()
                        except Produit.DoesNotExist:
                            continue

                    # 🧹 Nettoyage session
                    del request.session["panier"]
                    request.session.modified = True

                messages.success(request, "Connexion réussie.")
                next_url = request.GET.get('next')
                return redirect(next_url or 'home')
            else:
                messages.error(request, "Identifiants invalides.")
    else:
        form = ConnexionForm()

    return render(request, 'comptes/connexion.html', {'form': form})


def deconnexion_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')

@login_required
def profil_modifier_view(request):
    utilisateur = request.user

    if request.method == 'POST':
        form = ProfilForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect('profil')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProfilForm(instance=utilisateur)

    return render(request, 'comptes/profil_modifier.html', {'form': form})

@login_required
def profil_view(request):
    utilisateur = request.user
    return render(request, 'comptes/profil.html', {'utilisateur': utilisateur})
