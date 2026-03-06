from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class PrestacaoContaPTM(TimestampedModel):
    ptm = models.OneToOneField(PTM, on_delete=models.CASCADE, related_name="prestacao_conta")
    prazo_contas = models.DateField(null=True, blank=True)
    data_prestacao = models.DateField(null=True, blank=True)
    situacao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("ptm",)

    def __str__(self):
        return f"{self.ptm.ordem} - prestacao"


class PrestacaoContaHistorico(TimestampedModel):
    prestacao = models.ForeignKey(
        PrestacaoContaPTM,
        on_delete=models.CASCADE,
        related_name="historico",
    )
    data = models.DateField(null=True, blank=True)
    observacao = models.TextField()

    class Meta:
        ordering = ("data", "id")

    def __str__(self):
        return f"{self.prestacao.ptm.ordem} - {self.data}"
