import ptms.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ptms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ptm",
            name="public_access_token",
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="ptm",
            name="public_analysis_status",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.CreateModel(
            name="PublicDocumentPTM",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("nome_remetente", models.CharField(max_length=150)),
                ("contato", models.CharField(blank=True, max_length=150)),
                ("descricao", models.TextField(blank=True)),
                ("arquivo", models.FileField(upload_to=ptms.models.public_document_upload_to)),
                (
                    "ptm",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="documentos_publicos",
                        to="ptms.ptm",
                    ),
                ),
            ],
            options={
                "verbose_name": "Documento Publico do PTM",
                "verbose_name_plural": "Documentos Publicos do PTM",
                "ordering": ("-created_at",),
            },
        ),
    ]
