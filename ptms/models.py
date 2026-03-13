import secrets
from decimal import Decimal

from django.db import models

from core.models import AreaInvestimento, Secretaria, StatusObra, StatusPTM, TimestampedModel, TipoFEM


def generate_public_access_token():
    return secrets.token_urlsafe(24)


def public_document_upload_to(instance, filename):
    return f"ptms/publico/{instance.ptm_id}/{filename}"


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
    public_access_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    public_analysis_status = models.CharField(max_length=255, blank=True)

    populacao_beneficiada = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("ordem",)

    def __str__(self):
        return f"{self.ordem} - {self.municipio}"

    def ensure_public_access_token(self):
        if self.public_access_token:
            return self.public_access_token
        token = generate_public_access_token()
        while PTM.objects.filter(public_access_token=token).exists():
            token = generate_public_access_token()
        self.public_access_token = token
        return token


class PublicDocumentPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="documentos_publicos")
    nome_remetente = models.CharField(max_length=150)
    contato = models.CharField(max_length=150, blank=True)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to=public_document_upload_to)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Documento Publico do PTM"
        verbose_name_plural = "Documentos Publicos do PTM"

    def __str__(self):
        return f"{self.ptm.ordem} - {self.nome_remetente}"
