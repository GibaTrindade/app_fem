from django.db import models

from core.models import TimestampedModel
from ptms.models import PTM


class EventoPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="eventos")
    data_evento = models.DateField()
    descricao = models.TextField()
    status_ptm = models.ForeignKey("core.StatusPTM", on_delete=models.PROTECT)
    status_obra = models.ForeignKey("core.StatusObra", on_delete=models.PROTECT)

    class Meta:
        ordering = ("data_evento", "id")

    def __str__(self):
        return f"{self.ptm.ordem} - {self.data_evento}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ptm.status_ptm_atual = self.status_ptm
        self.ptm.status_obra_atual = self.status_obra
        self.ptm.save(update_fields=["status_ptm_atual", "status_obra_atual", "updated_at"])
