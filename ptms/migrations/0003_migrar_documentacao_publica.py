import django.db.models.deletion
from django.db import migrations, models


def migrar_status_analise(apps, schema_editor):
    PTM = apps.get_model("ptms", "PTM")
    StatusAnaliseDocumentacao = apps.get_model("core", "StatusAnaliseDocumentacao")

    for ptm in PTM.objects.exclude(public_analysis_status="").iterator():
        status_nome = (ptm.public_analysis_status or "").strip()
        if not status_nome:
            continue
        status_obj, _ = StatusAnaliseDocumentacao.objects.get_or_create(nome=status_nome)
        ptm.status_analise_documentacao_id = status_obj.id
        ptm.save(update_fields=["status_analise_documentacao"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_statusanalisedocumentacao"),
        ("ptms", "0002_ptm_public_access_and_documents"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ptm",
            old_name="public_access_token",
            new_name="codigo_acesso_publico",
        ),
        migrations.AddField(
            model_name="ptm",
            name="status_analise_documentacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ptms_status_analise_documentacao",
                to="core.statusanalisedocumentacao",
            ),
        ),
        migrations.RunPython(migrar_status_analise, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="ptm",
            name="public_analysis_status",
        ),
        migrations.RenameModel(
            old_name="PublicDocumentPTM",
            new_name="DocumentoPublicoPTM",
        ),
    ]
