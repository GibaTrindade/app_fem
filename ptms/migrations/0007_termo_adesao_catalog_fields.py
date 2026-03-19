from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_termo_adesao_catalogos"),
        ("ptms", "0006_termoadesaoptm_remove_ptm_termo_adesao"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="termoadesaoptm",
            name="observacao",
        ),
        migrations.RemoveField(
            model_name="termoadesaoptm",
            name="responsavel",
        ),
        migrations.AddField(
            model_name="termoadesaoptm",
            name="observacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="termos_adesao",
                to="core.termoadesaoobservacao",
            ),
        ),
        migrations.AddField(
            model_name="termoadesaoptm",
            name="responsavel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="termos_adesao",
                to="core.termoadesaoresponsavel",
            ),
        ),
    ]
