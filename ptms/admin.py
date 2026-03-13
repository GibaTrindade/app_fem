from django.contrib import admin

from .models import PTM, PublicDocumentPTM


@admin.register(PTM)
class PTMAdmin(admin.ModelAdmin):
    list_display = (
        "ordem",
        "municipio",
        "regiao",
        "tipo_fem",
        "status_ptm_atual",
        "status_obra_atual",
        "public_analysis_status",
    )
    search_fields = ("ordem", "municipio", "projeto")
    list_filter = ("regiao", "tipo_fem", "status_ptm_atual", "status_obra_atual", "secretaria")


@admin.register(PublicDocumentPTM)
class PublicDocumentPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "nome_remetente", "contato", "created_at")
    search_fields = ("ptm__ordem", "ptm__municipio", "nome_remetente", "contato")
