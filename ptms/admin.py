from django.contrib import admin

from .models import DocumentoPublicoPTM, PTM


@admin.register(PTM)
class PTMAdmin(admin.ModelAdmin):
    list_display = (
        "ordem",
        "municipio",
        "regiao",
        "tipo_fem",
        "status_ptm_atual",
        "status_obra_atual",
        "status_analise_documentacao",
    )
    search_fields = ("ordem", "municipio", "projeto")
    list_filter = (
        "regiao",
        "tipo_fem",
        "status_ptm_atual",
        "status_obra_atual",
        "status_analise_documentacao",
        "secretaria",
    )


@admin.register(DocumentoPublicoPTM)
class DocumentoPublicoPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "nome_remetente", "contato", "created_at")
    search_fields = ("ptm__ordem", "ptm__municipio", "nome_remetente", "contato")
