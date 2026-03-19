from django.db import migrations, models


OBSERVACOES_INICIAIS = [
    "PTM INICIAL EM ANÁLISE",
    "PTM INICIAL COM PENDÊNCIAS",
    "AGUARDANDO FORMALIZAÇÃO DO TERMO ADITIVO",
    "AGUARDANDO ASSINATURA DO TERMO ADITIVO",
    "AGUARDANDO LIBERAÇÃO DA SEFAZ PARA PAGAMENTO DA PARCELA",
    "REPROGRAMAÇÃO EM ANÁLISE",
    "REPROGRAMAÇÃO COM PENDÊNCIAS",
    "VISTORIA E PARECER FINANCEIRO EM ANÁLISE",
    "VISTORIA OK E PARECER FINANCEIRO EM ANÁLISE",
    "VISTORIA OK E PARECER FINANCEIRO COM PENDÊNCIAS",
    "AGUARDANDO MUNICÍPIO SOLICITAR PARCELA",
    "PTM CANCELADO",
    "AGUARDANDO MUNICÍPIO ENVIAR PRESTAÇÃO DE CONTAS",
    "PRESTAÇÃO DE CONTAS EM ANÁLISE",
    "PRESTAÇÃO DE CONTAS COM PENDÊNCIAS",
    "PRESTAÇÃO DE CONTAS REPROVADA APÓS 4ª ANÁLISE",
    "PRESTAÇÃO DE CONTAS APROVADA",
    "PRESTAÇÃO DE CONTAS APROVADA COM RESSALVA",
]


RESPONSAVEIS_INICIAIS = [
    "SEPLAG",
    "CEHAB",
    "SEINFRA",
    "SES",
    "SEE",
    "SECMULHER",
    "SEDUH",
    "SDS",
    "SDSCJPVD",
    "MUNICÍPIO",
]


def seed_catalogos(apps, schema_editor):
    Observacao = apps.get_model("core", "TermoAdesaoObservacao")
    Responsavel = apps.get_model("core", "TermoAdesaoResponsavel")
    for nome in OBSERVACOES_INICIAIS:
        Observacao.objects.get_or_create(nome=nome)
    for nome in RESPONSAVEIS_INICIAIS:
        Responsavel.objects.get_or_create(nome=nome)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_statusanalisedocumentacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="TermoAdesaoObservacao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("nome", models.CharField(max_length=255, unique=True)),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("nome",),
            },
        ),
        migrations.CreateModel(
            name="TermoAdesaoResponsavel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("nome", models.CharField(max_length=255, unique=True)),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("nome",),
            },
        ),
        migrations.RunPython(seed_catalogos, migrations.RunPython.noop),
    ]
