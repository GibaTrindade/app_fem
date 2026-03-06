from decimal import Decimal

from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class PagamentoPTM(TimestampedModel):
    TIPO_REGISTRO_CHOICES = (
        ("normal", "Normal"),
        ("extra", "Extra"),
    )

    PARCELA_CHOICES = (
        ("1", "1a"),
        ("2", "2a"),
        ("3", "3a"),
        ("4", "4a"),
    )

    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="pagamentos")
    parcela = models.CharField(max_length=2, choices=PARCELA_CHOICES)
    tipo_registro = models.CharField(max_length=10, choices=TIPO_REGISTRO_CHOICES, default="normal")

    dt_solicitacao = models.DateField(null=True, blank=True)
    dt_envio_pg = models.DateField(null=True, blank=True)
    dt_pagamento = models.DateField(null=True, blank=True)

    valor_previsto = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    valor_realizado = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    numero_ob = models.CharField(max_length=50, blank=True)
    numero_empenho = models.CharField(max_length=50, blank=True)
    observacao = models.TextField(blank=True)

    class Meta:
        ordering = ("ptm", "parcela", "dt_pagamento", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - parcela {self.parcela}"
