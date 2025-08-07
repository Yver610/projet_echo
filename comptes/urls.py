from django.urls import path
from .views import inscription_view, connexion_view, deconnexion_view, profil_view
from . import views

urlpatterns = [
    path('inscription/', inscription_view, name='inscription'),
    path('connexion/', connexion_view, name='connexion'),
    path('deconnexion/', deconnexion_view, name='deconnexion'),
    path('profil/', views.profil_view, name='profil'),
    path('profil/modifier/', views.profil_modifier_view, name='profil_modifier'),
]
