# Generated by Django 4.0.5 on 2022-07-22 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offer_service', '0001_new_notifications_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]