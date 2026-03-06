from django.contrib import admin

from .models import VistoriaPTM


@admin.register(VistoriaPTM)
class VistoriaPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "dt_solicitacao", "dt_resposta", "percentual_execucao")
    search_fields = ("ptm__ordem", "ptm__municipio", "observacao")
    list_filter = ("dt_solicitacao",)
