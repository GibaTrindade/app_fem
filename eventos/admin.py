from django.contrib import admin

from .models import EventoPTM


@admin.register(EventoPTM)
class EventoPTMAdmin(admin.ModelAdmin):
    list_display = ("ptm", "data_evento", "status_ptm", "status_obra")
    search_fields = ("ptm__ordem", "ptm__municipio", "descricao")
    list_filter = ("status_ptm", "status_obra", "data_evento")
