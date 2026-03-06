from decimal import Decimal

from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class VistoriaPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="vistorias")
    ordem_vistoria = models.PositiveSmallIntegerField(default=1)
    dt_solicitacao = models.DateField(null=True, blank=True)
    dt_resposta = models.DateField(null=True, blank=True)
    percentual_execucao = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.0000"))
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ("ptm", "ordem_vistoria", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - vistoria {self.id}"

    @property
    def percentual_execucao_formatado(self) -> str:
        valor = (self.percentual_execucao or Decimal("0.0000")) * Decimal("100")
        valor = valor.quantize(Decimal("0.01"))
        texto = format(valor, "f").rstrip("0").rstrip(".")
        return f"{texto}%"
