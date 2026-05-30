from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pigeons', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pigeon',
            name='pedigree_image',
            field=models.ImageField(
                blank=True, null=True,
                upload_to='pedigree/',
                help_text='Photo of pedigree certificate or chart'
            ),
        ),
    ]
