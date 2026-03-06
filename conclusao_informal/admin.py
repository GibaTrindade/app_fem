from django.contrib import admin

from .models import ConclusaoInformalPTM


@admin.register(ConclusaoInformalPTM)
class ConclusaoInformalPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "percentual_declarado", "data", "contato")
    search_fields = ("ptm__ordem", "ptm__municipio", "contato", "observacao")
    list_filter = ("data",)
