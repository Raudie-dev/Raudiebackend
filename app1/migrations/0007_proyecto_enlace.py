from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0006_noticia'),
    ]

    operations = [
        migrations.AddField(
            model_name='proyecto',
            name='enlace',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
    ]
