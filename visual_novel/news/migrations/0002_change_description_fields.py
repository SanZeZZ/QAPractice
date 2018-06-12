# Generated by Django 2.0.2 on 2018-06-10 14:37

from django.db import migrations, models
import sanitizer.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='description',
            field=sanitizer.models.SanitizedTextField(blank=True, default='', max_length=6000, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='news',
            name='short_description',
            field=models.CharField(blank=True, default='', max_length=512, verbose_name='Краткое описание'),
        ),
    ]