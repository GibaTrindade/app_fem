from decimal import Decimal

from django.db import models

from core.models import AreaInvestimento, Secretaria, StatusObra, StatusPTM, TimestampedModel, TipoFEM


class PTM(TimestampedModel):
    ordem = models.CharField(max_length=30, unique=True)
    regiao = models.CharField(max_length=120)
    municipio = models.CharField(max_length=120)
    projeto = models.TextField()
    projeto_detalhado = models.TextField(blank=True)

    tipo_fem = models.ForeignKey(TipoFEM, on_delete=models.PROTECT)
    status_ptm_atual = models.ForeignKey(
        StatusPTM,
        on_delete=models.PROTECT,
        related_name="ptms_status_ptm",
        null=True,
        blank=True,
    )
    status_obra_atual = models.ForeignKey(
        StatusObra,
        on_delete=models.PROTECT,
        related_name="ptms_status_obra",
        null=True,
        blank=True,
    )

    data_final = models.DateField(null=True, blank=True)
    data_aprovacao = models.DateField(null=True, blank=True)

    teto_fem = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    investimento_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    recurso_fem = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    rendimentos_fem = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    contrapartida = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    ressalva = models.TextField(blank=True)
    secretaria = models.ForeignKey(Secretaria, on_delete=models.PROTECT, null=True, blank=True)
    area_investimento = models.ForeignKey(AreaInvestimento, on_delete=models.PROTECT, null=True, blank=True)
    conta_ptm = models.CharField(max_length=50, blank=True)
    descricao = models.TextField(blank=True)

    populacao_beneficiada = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("ordem",)

    def __str__(self):
        return f"{self.ordem} - {self.municipio}"
