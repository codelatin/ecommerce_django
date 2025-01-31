from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Auth
# Register your models here.


class AuthAdmin(UserAdmin):
    list_display =('email','nombre','apellido','username','ultimo_login','fecha_registro','is_active',)
    list_display_links =('email','nombre','apellido')
    readonly_fields=('ultimo_login','fecha_registro')
    ordering=('-fecha_registro',)
    filter_horizontal=()
    list_filter=()
    fieldsets=()

admin.site.register(Auth, AuthAdmin)



