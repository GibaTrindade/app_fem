from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NomeCatalogo(TimestampedModel):
    nome = models.CharField(max_length=255, unique=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ("nome",)

    def __str__(self):
        return self.nome


class TipoFEM(NomeCatalogo):
    pass


class StatusPTM(NomeCatalogo):
    pass


class StatusObra(NomeCatalogo):
    pass


class AreaInvestimento(NomeCatalogo):
    pass


class Secretaria(NomeCatalogo):
    pass


class Municipio(NomeCatalogo):
    pass


class UserMunicipio(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_municipios",
    )
    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.CASCADE,
        related_name="usuarios_vinculados",
    )

    class Meta:
        unique_together = ("user", "municipio")
        ordering = ("user__username", "municipio__nome")
        verbose_name = "Vinculo Usuario-Municipio"
        verbose_name_plural = "Vinculos Usuario-Municipio"

    def __str__(self):
        return f"{self.user} - {self.municipio}"
