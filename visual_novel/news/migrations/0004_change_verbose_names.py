# Generated by Django 2.0.2 on 2018-07-30 08:42

from django.db import migrations
import sanitizer.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_change_short_description_to_sanitilized_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='description',
            field=sanitizer.models.SanitizedTextField(blank=True, default='', help_text='Допустимо использовать html-теги <b>a</b>, <b>p</b>, <b>img</b>, <b>table</b>, <b>tr</b>, <b>td</b>, <b>th</b>, <b>tbody</b>, <b>thead</b>, <b>span</b>, <b>div</b>, <b>br</b>, <b>b</b>, <b>i</b> и парамеры <b>href</b>, <b>src</b>, <b>style</b>, <b>title</b>', max_length=6000, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='news',
            name='short_description',
            field=sanitizer.models.SanitizedTextField(blank=True, default='', help_text='Допустимо использовать html-теги <b>a</b>, <b>p</b>, <b>img</b>, <b>table</b>, <b>tr</b>, <b>td</b>, <b>th</b>, <b>tbody</b>, <b>thead</b>, <b>span</b>, <b>div</b>, <b>br</b>, <b>b</b>, <b>i</b> и парамеры <b>href</b>, <b>src</b>, <b>style</b>, <b>title</b>', max_length=512, verbose_name='Краткое описание'),
        ),
    ]