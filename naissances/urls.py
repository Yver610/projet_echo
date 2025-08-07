from django.urls import path
from .views import page_naissances
from .views import reserver_chiot

urlpatterns = [
    path('', page_naissances, name='liste_portees'),
    path('reserver/<int:chiot_id>/', reserver_chiot, name='reserver_chiot'),
]
