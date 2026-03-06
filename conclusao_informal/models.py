from decimal import Decimal

from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class ConclusaoInformalPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="conclusoes_informais")
    percentual_declarado = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.0000"))
    data = models.DateField(null=True, blank=True)
    contato = models.CharField(max_length=255, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ("data", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - {self.percentual_declarado}"
