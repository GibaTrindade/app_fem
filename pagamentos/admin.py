from django.contrib import admin

from .models import PagamentoPTM


@admin.register(PagamentoPTM)
class PagamentoPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "parcela", "tipo_registro", "valor_realizado", "dt_pagamento")
    search_fields = ("ptm__ordem", "ptm__municipio", "numero_ob", "numero_empenho")
    list_filter = ("parcela", "tipo_registro")
