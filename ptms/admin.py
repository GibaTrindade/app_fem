from django.contrib import admin

from .models import PTM


@admin.register(PTM)
class PTMAdmin(admin.ModelAdmin):
    list_display = ("ordem", "municipio", "regiao", "tipo_fem", "status_ptm_atual", "status_obra_atual")
    search_fields = ("ordem", "municipio", "projeto")
    list_filter = ("regiao", "tipo_fem", "status_ptm_atual", "status_obra_atual", "secretaria")
