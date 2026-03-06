from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import AreaInvestimento, Municipio, Secretaria, StatusObra, StatusPTM, TipoFEM, UserMunicipio

User = get_user_model()


class UserMunicipioInline(admin.TabularInline):
    model = UserMunicipio
    extra = 1
    raw_id_fields = ("municipio",)
    show_change_link = True


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [UserMunicipioInline]


@admin.register(TipoFEM)
class TipoFEMAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(StatusPTM)
class StatusPTMAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(StatusObra)
class StatusObraAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(AreaInvestimento)
class AreaInvestimentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(Secretaria)
class SecretariaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(Municipio)
class MunicipioAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)


@admin.register(UserMunicipio)
class UserMunicipioAdmin(admin.ModelAdmin):
    list_display = ("user", "municipio", "created_at")
    search_fields = ("user__username", "municipio__nome")
    list_filter = ("municipio",)
    raw_id_fields = ("user", "municipio")
