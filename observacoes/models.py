from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class ObservacaoEncaminhamentoPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="observacoes_enc")
    data = models.DateField(null=True, blank=True)
    observacao = models.TextField()
    origem = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ("data", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - {self.data}"
