"""
URL configuration for elevage_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from elevage_site.views import home, a_propos
from boutique.views import panier_view, commande_view, boutique_view
from elevage_site.views import home  # ton ancienne vue home

urlpatterns = [
    path('admin/', admin.site.urls),
     path('', boutique_view, name='home'),         # 👈 la boutique devient l'accueil
    path('accueil/', home, name='accueil'),
    path('panier/', panier_view, name='panier'),
    path('commande/', commande_view, name='commande'),
    path('a-propos/', a_propos, name='a_propos'),  
    path('naissances/', include('naissances.urls')),
    path('contact/', include('contact.urls')),
    path('comptes/', include('comptes.urls')),
    path('boutique/', include('boutique.urls')),
]

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)