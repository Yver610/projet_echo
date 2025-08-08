from django.contrib import admin
from .models import Produit, Panier, ProduitsPanier, Commande, LigneCommande
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import TabularInline

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'en_stock', 'seuil_alerte', 'actif', 'stock_critique')
    list_filter = ['actif', 'stock']  # Tu peux ajouter d'autres filtres utiles
    search_fields = ('nom',)

    @admin.display(boolean=True, description="Stock critique")
    def stock_critique(self, obj):
        return obj.stock <= obj.seuil_alerte

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'nombre_articles', 'total_panier')

    def nombre_articles(self, obj):
        return sum([p.quantite for p in obj.produits.all()])
    nombre_articles.short_description = "Quantité totale"

    def total_panier(self, obj):
        total = sum([p.produit.prix * p.quantite for p in obj.produits.all()])
        return f"{total:.2f} €"
    total_panier.short_description = "Total"


@admin.register(ProduitsPanier)
class ProduitsPanierAdmin(admin.ModelAdmin):
    list_display = ('lien_panier', 'lien_produit', 'quantite', 'afficher_sous_total')

    def lien_panier(self, obj):
        url = reverse('admin:boutique_panier_change', args=[obj.panier.id])
        return format_html('<a href="{}">Panier #{}</a>', url, obj.panier.id)
    lien_panier.short_description = "Panier"

    def lien_produit(self, obj):
        url = reverse('admin:boutique_produit_change', args=[obj.produit.id])
        return format_html('<a href="{}">{}</a>', url, obj.produit.nom)
    lien_produit.short_description = "Produit"

    def afficher_sous_total(self, obj):
        return f"{obj.produit.prix * obj.quantite:.2f} €"
    afficher_sous_total.short_description = "Sous-total"

class LigneCommandeInline(TabularInline):
    model = LigneCommande
    extra = 0  # pas de lignes vides supplémentaires
    readonly_fields = ('produit', 'quantite', 'prix_unitaire', 'get_total')
    fields = ('produit', 'quantite', 'prix_unitaire', 'get_total')
    can_delete = False

    def get_total(self, obj):
        return f"{obj.get_total_ligne():.2f} €"
    get_total.short_description = "Total ligne"

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'date_commande', 'statut', 'total')
    list_editable = ('statut',)
    list_filter = ('statut', 'date_commande')
    search_fields = ('utilisateur__email',)
    inlines = [LigneCommandeInline]

@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire', 'get_total')

    def get_total(self, obj):
        return f"{obj.get_total_ligne():.2f} €"
    get_total.short_description = "Total ligne"

