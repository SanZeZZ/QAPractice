# Generated by Django 2.0.2 on 2018-03-25 14:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0004_reverse_dependency_on_translation_links'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translationitem',
            name='statistics',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='translation.TranslationStatistics', verbose_name='Привязанная статистика'),
        ),
        migrations.AlterField(
            model_name='translationitem',
            name='visual_novel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vn_core.VisualNovel', verbose_name='Визуальная новелла'),
        ),
    ]
