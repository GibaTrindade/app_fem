from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vistorias", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="vistoriaptm",
            name="ordem_vistoria",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterModelOptions(
            name="vistoriaptm",
            options={"ordering": ("ptm", "ordem_vistoria", "id")},
        ),
    ]
