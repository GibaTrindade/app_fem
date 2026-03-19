from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ptms", "0005_ptm_termo_adesao"),
    ]

    operations = [
        migrations.CreateModel(
            name="TermoAdesaoPTM",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sei", models.CharField(blank=True, max_length=120)),
                ("data", models.DateField(blank=True, null=True)),
                ("responsavel", models.CharField(blank=True, max_length=150)),
                ("observacao", models.TextField(blank=True)),
                ("secretaria", models.CharField(blank=True, max_length=150)),
                (
                    "ptm",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="termo_adesao_registro",
                        to="ptms.ptm",
                    ),
                ),
            ],
            options={
                "verbose_name": "Termo de Adesao do PTM",
                "verbose_name_plural": "Termos de Adesao dos PTMs",
                "ordering": ("ptm__ordem",),
            },
        ),
        migrations.RemoveField(
            model_name="ptm",
            name="termo_adesao",
        ),
    ]
