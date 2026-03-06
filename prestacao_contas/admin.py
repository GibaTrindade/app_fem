from django.contrib import admin

from .models import PrestacaoContaHistorico, PrestacaoContaPTM


class PrestacaoContaHistoricoInline(admin.TabularInline):
    model = PrestacaoContaHistorico
    extra = 0


@admin.register(PrestacaoContaPTM)
class PrestacaoContaPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "prazo_contas", "data_prestacao", "situacao")
    search_fields = ("ptm__ordem", "ptm__municipio", "situacao")
    inlines = (PrestacaoContaHistoricoInline,)
