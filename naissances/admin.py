from django.contrib import admin
from .models import Portee, Chiot
from .models import Reservation
from django.db import models
from django.forms import DateInput

class ChiotInline(admin.TabularInline):
    model = Chiot
    extra = 1

@admin.register(Portee)
class PorteeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_naissance')
    inlines = [ChiotInline]

@admin.register(Chiot)
class ChiotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'race', 'portee', 'prix', 'disponible')
    list_filter = ('disponible', 'race', 'portee')
    search_fields = ('nom', 'race')

class PorteeAdmin(admin.ModelAdmin):
    formfield_overrides = {
    models.DateField: {'widget': DateInput(attrs={'type': 'date'})},
}


admin.site.register(Reservation)