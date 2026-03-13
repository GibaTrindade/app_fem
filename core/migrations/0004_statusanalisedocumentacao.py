from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_usermunicipio"),
    ]

    operations = [
        migrations.CreateModel(
            name="StatusAnaliseDocumentacao",
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
    ]
