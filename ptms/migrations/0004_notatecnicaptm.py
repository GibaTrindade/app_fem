from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ptms", "0003_migrar_documentacao_publica"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotaTecnicaPTM",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("observacao", models.TextField(blank=True)),
                (
                    "ptm",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nota_tecnica",
                        to="ptms.ptm",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notas_tecnicas_ptm_atualizadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Nota Tecnica do PTM",
                "verbose_name_plural": "Notas Tecnicas dos PTMs",
                "ordering": ("ptm__ordem",),
            },
        ),
    ]
