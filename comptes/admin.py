from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'prenom', 'nom', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'newsletter')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('prenom', 'nom', 'email', 'telephone', 'adresse_postale', 'adresse_facturation', 'civilite')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'prenom', 'nom', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email', 'prenom', 'nom')
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
