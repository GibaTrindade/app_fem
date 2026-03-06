from decimal import Decimal

from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class VistoriaPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="vistorias")
    dt_solicitacao = models.DateField(null=True, blank=True)
    dt_resposta = models.DateField(null=True, blank=True)
    percentual_execucao = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.0000"))
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ("ptm", "dt_solicitacao", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - vistoria {self.id}"
