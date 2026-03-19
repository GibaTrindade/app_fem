from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ptms", "0004_notatecnicaptm"),
    ]

    operations = [
        migrations.AddField(
            model_name="ptm",
            name="termo_adesao",
            field=models.TextField(blank=True),
        ),
    ]
