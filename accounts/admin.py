from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations EpiTEC', {'fields': ('role', 'region')}),
    )
    list_display = ('username', 'role', 'region', 'is_staff')

admin.site.register(Utilisateur, UtilisateurAdmin)