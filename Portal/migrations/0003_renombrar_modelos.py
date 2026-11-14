from django.db import migrations


class Migration(migrations.Migration):
    """Renombra modelos y campos a la convención de Python (PascalCase)."""

    dependencies = [
        ("Portal", "0002_metodo_de_pago"),
    ]

    operations = [
        migrations.RenameModel(old_name="Linea_servicio", new_name="LineaServicio"),
        migrations.RenameModel(old_name="Metodo_de_pago", new_name="MetodoDePago"),
        migrations.RenameField(model_name="metododepago", old_name="cliente", new_name="clientes"),
    ]
