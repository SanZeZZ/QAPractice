# Generated by Django 2.0.2 on 2018-08-23 09:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_beat', '0006_auto_20180210_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailingTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('send_hour', models.IntegerField(validators=[django.core.validators.MaxValueValidator(23), django.core.validators.MinValueValidator(0)], verbose_name='Час рассылки')),
                ('send_weekday', models.IntegerField(validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)], verbose_name='Час рассылки')),
                ('mailing_task', models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='django_celery_beat.PeriodicTask', verbose_name='Задача автоматичесой рассылки')),
            ],
            options={
                'verbose_name': 'Рассылка статистики',
                'verbose_name_plural': 'Рассылки статистики',
            },
        ),
    ]