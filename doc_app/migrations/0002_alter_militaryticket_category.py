# Generated by Django 4.2.6 on 2023-12-12 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='militaryticket',
            name='category',
            field=models.CharField(choices=[('A', 'А - Годен'), ('B', 'Б - Годен с небольшими ограничениями'), ('C', 'В - Ограниченно годен'), ('D', 'Г - Временно не годен'), ('E', 'Д - Не годен')], max_length=40, verbose_name='Призывная категория'),
        ),
    ]
