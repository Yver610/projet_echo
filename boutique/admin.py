from django.contrib import admin
from django.db import models
from .models import Produit, Panier, ProduitsPanier, Commande, LigneCommande
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import TabularInline, SimpleListFilter
from django.utils.safestring import mark_safe

class StockCritiqueFilter(SimpleListFilter):
    title = 'État du stock'
    parameter_name = 'etat_stock'

    def lookups(self, request, model_admin):
        return (
            ('rupture', '❌ Rupture de stock'),
            ('bas', '⚠️ Stock bas'),
            ('ok', '✅ Stock suffisant'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'rupture':
            return queryset.filter(stock=0)
        if self.value() == 'bas':
            return queryset.filter(stock__gt=0, stock__lte=models.F('seuil_alerte'))
        if self.value() == 'ok':
            return queryset.filter(stock__gt=models.F('seuil_alerte'))

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'en_stock', 'seuil_alerte', 'actif', 'alerte_stock')
    list_editable = ('seuil_alerte',)
    list_filter = ['actif', StockCritiqueFilter]
    readonly_fields = ('apercu_image',)
    search_fields = ('nom',)
    fieldsets = (
    ("Informations produit", {
        "fields": ("nom", "prix", "description","apercu_image")
    }),
    ("Stock et seuils", {
        "fields": ("stock", "seuil_alerte")
    }),
    ("Publication", {
        "fields": ("actif",)
    }),
    )

    @admin.display(description="Alerte stock")
    def alerte_stock(self, obj):
        if obj.stock <= 0 and obj.actif:
            return format_html('<span style="color:red;font-weight:bold;">❌ Rupture (actif)</span>')
        elif obj.stock <= obj.seuil_alerte:
            return format_html('<span style="color:orange;font-weight:bold;">⚠️ Stock bas ({})</span>', obj.stock)
        return format_html('<span style="color:green;">✅ OK ({})</span>', obj.stock)

    @admin.display(description="Aperçu image")
    def apercu_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 150px;" />', obj.image.url)
        return "Pas d'image"

class ProduitsPanierInline(admin.TabularInline):
    model = ProduitsPanier
    extra = 0
    readonly_fields = ('produit', 'quantite', 'afficher_sous_total')
    fields = ('produit', 'quantite', 'afficher_sous_total')

    def afficher_sous_total(self, obj):
        return f"{obj.produit.prix * obj.quantite:.2f} €"
    afficher_sous_total.short_description = "Sous-total"

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur_affiche', 'nombre_articles', 'total_panier')
    inlines = [ProduitsPanierInline]

    def nombre_articles(self, obj):
        return sum([p.quantite for p in obj.produits.all()])
    nombre_articles.short_description = "Quantité totale"

    def total_panier(self, obj):
        total = sum([p.produit.prix * p.quantite for p in obj.produits.all()])
        return f"{total:.2f} €"
    total_panier.short_description = "Total"

    @admin.display(description="Utilisateur")
    def utilisateur_affiche(self, obj):
        if obj.utilisateur:
            return f"{obj.utilisateur.get_full_name()} ({obj.utilisateur.email})"
        return "Utilisateur anonyme"
    


@admin.register(ProduitsPanier)
class ProduitsPanierAdmin(admin.ModelAdmin):
    list_display = ('lien_panier', 'lien_produit', 'quantite', 'afficher_sous_total', 'etat_stock')

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

    @admin.display(description="État du stock")
    def etat_stock(self, obj):
        if obj.produit.stock < obj.quantite:
            return format_html('<span style="color:red;font-weight:bold;">Insuffisant</span>')
        return format_html('<span style="color:green;">OK</span>')

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
    list_display = ('id', 'utilisateur', 'date_commande', 'statut', 'statut_color', 'total', 'voir_details')
    list_editable = ('statut',)
    list_filter = ('statut', 'date_commande')
    search_fields = ('utilisateur__email',)
    inlines = [LigneCommandeInline]

    @admin.display(description="Statut (visuel)")
    def statut_color(self, obj):
        color_map = {
            'en_attente': 'orange',
            'payée': 'green',
            'expédiée': 'cyan', 
            'annulée': 'red',
        }
        color = color_map.get(obj.statut, 'black')
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, obj.get_statut_display())

    @admin.display(description="Actions")
    def voir_details(self, obj):
        url = reverse('admin:boutique_commande_change', args=[obj.id])
        return format_html('<a class="button" href="{}">Voir détails</a>', url)
    
@admin.register(LigneCommande)
class LigneCommandeAdmin(admin.ModelAdmin):
    list_display = ('commande', 'produit', 'quantite', 'prix_unitaire', 'get_total')
    autocomplete_fields = ('produit',)
    
    def get_total(self, obj):
        return f"{obj.get_total_ligne():.2f} €"
    get_total.short_description = "Total ligne"

