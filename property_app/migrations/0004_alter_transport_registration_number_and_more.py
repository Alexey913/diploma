# Generated by Django 4.2.6 on 2023-12-12 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property_app', '0003_alter_realty_description_alter_realty_type_property_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transport',
            name='registration_number',
            field=models.CharField(blank=True, max_length=9, null=True, verbose_name='Регистрационный номер'),
        ),
        migrations.AlterField(
            model_name='transport',
            name='year_release',
            field=models.IntegerField(verbose_name='Год выпуска ТС'),
        ),
    ]
