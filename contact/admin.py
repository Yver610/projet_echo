from django.contrib import admin
from .models import MessageContact

@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'date_envoi')
    readonly_fields = ('nom', 'email', 'message', 'date_envoi')
