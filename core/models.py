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
