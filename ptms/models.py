import secrets
from decimal import Decimal

from django.conf import settings
from django.db import models

from core.models import (
    AreaInvestimento,
    Secretaria,
    StatusAnaliseDocumentacao,
    StatusObra,
    StatusPTM,
    TermoAdesaoObservacao,
    TermoAdesaoResponsavel,
    TimestampedModel,
    TipoFEM,
)


def gerar_codigo_acesso_publico():
    return secrets.token_urlsafe(24)


def upload_documento_publico_ptm(instance, filename):
    return f"ptms/publico/{instance.ptm_id}/{filename}"


# Compatibilidade com migracoes ja aplicadas.
generate_public_access_token = gerar_codigo_acesso_publico
public_document_upload_to = upload_documento_publico_ptm


class PTM(TimestampedModel):
    ordem = models.CharField(max_length=30, unique=True)
    regiao = models.CharField(max_length=120)
    municipio = models.CharField(max_length=120)
    projeto = models.TextField()
    projeto_detalhado = models.TextField(blank=True)
    deputado = models.CharField(max_length=200, blank=True)
    numero_emenda = models.CharField(max_length=255, blank=True)

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
    codigo_acesso_publico = models.CharField(max_length=64, unique=True, null=True, blank=True)
    status_analise_documentacao = models.ForeignKey(
        StatusAnaliseDocumentacao,
        on_delete=models.PROTECT,
        related_name="ptms_status_analise_documentacao",
        null=True,
        blank=True,
    )

    populacao_beneficiada = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ("ordem",)

    def __str__(self):
        return f"{self.ordem} - {self.municipio}"

    def garantir_codigo_acesso_publico(self):
        if self.codigo_acesso_publico:
            return self.codigo_acesso_publico
        token = gerar_codigo_acesso_publico()
        while PTM.objects.filter(codigo_acesso_publico=token).exists():
            token = gerar_codigo_acesso_publico()
        self.codigo_acesso_publico = token
        return token


class DocumentoPublicoPTM(TimestampedModel):
    ptm = models.ForeignKey(PTM, on_delete=models.CASCADE, related_name="documentos_publicos")
    nome_remetente = models.CharField(max_length=150)
    contato = models.CharField(max_length=150, blank=True)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to=upload_documento_publico_ptm)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Documento Publico do PTM"
        verbose_name_plural = "Documentos Publicos do PTM"

    def __str__(self):
        return f"{self.ptm.ordem} - {self.nome_remetente}"


class NotaTecnicaPTM(TimestampedModel):
    ptm = models.OneToOneField(PTM, on_delete=models.CASCADE, related_name="nota_tecnica")
    observacao = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notas_tecnicas_ptm_atualizadas",
    )

    class Meta:
        ordering = ("ptm__ordem",)
        verbose_name = "Nota Tecnica do PTM"
        verbose_name_plural = "Notas Tecnicas dos PTMs"

    def __str__(self):
        return f"{self.ptm.ordem} - Nota Tecnica"


class TermoAdesaoPTM(TimestampedModel):
    ptm = models.OneToOneField(PTM, on_delete=models.CASCADE, related_name="termo_adesao_registro")
    sei = models.CharField(max_length=120, blank=True)
    data = models.DateField(null=True, blank=True)
    responsavel = models.ForeignKey(
        TermoAdesaoResponsavel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="termos_adesao",
    )
    observacao = models.ForeignKey(
        TermoAdesaoObservacao,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="termos_adesao",
    )
    secretaria = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ("ptm__ordem",)
        verbose_name = "Termo de Adesao do PTM"
        verbose_name_plural = "Termos de Adesao dos PTMs"

    def __str__(self):
        return f"{self.ptm.ordem} - Termo de Adesao"
