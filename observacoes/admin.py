from django.contrib import admin

from .models import ObservacaoEncaminhamentoPTM


@admin.register(ObservacaoEncaminhamentoPTM)
class ObservacaoEncaminhamentoPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "data", "origem")
    search_fields = ("ptm__ordem", "ptm__municipio", "observacao", "origem")
    list_filter = ("origem",)
