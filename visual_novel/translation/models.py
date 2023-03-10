import arrow

from django.conf import settings
from django.db import models
from django.db.models import Sum, Max
from django.contrib.auth.models import User
from django.urls import reverse

from bitfield import BitField
from mptt.models import MPTTModel, TreeForeignKey

from .choices import TRANSLATION_ITEMS_STATUSES
from cinfo.translators.models import Translator
from core.models import PublishModel, Profile
from vn_core.models import VisualNovel

TRANSLATION_ITEM_ACTIVE_BITCODE = 1


class TranslationStatistics(models.Model):
    tree_id = models.IntegerField(default=0)
    pictures_statistics = models.TextField(verbose_name='Статистика изображений', max_length=500, default='', blank=True)
    technical_statistics = models.TextField(verbose_name='Статистика тех. части', max_length=500, default='', blank=True)
    comment = models.TextField(verbose_name='Статистика изображений', max_length=2000, default='', blank=True)
    last_update = models.DateTimeField(verbose_name='Дата последнего обновления',
                                       auto_now_add=True, null=True, blank=True)
    total_rows = models.IntegerField(default=0, verbose_name='Всего строк')
    translated = models.IntegerField(default=0, verbose_name='Переведено')
    edited_first_pass = models.IntegerField(default=0, verbose_name='Первый проход редактуры')
    edited_second_pass = models.IntegerField(default=0, verbose_name='Второй проход редактуры')

    class Meta:
        db_table = 'statistics_item'

    def __str__(self):
        return f'Статистика перевода {self.tree_id}'


class TranslationStatisticsChapter(MPTTModel):
    title = models.CharField(max_length=50, verbose_name='Пользовательское название')
    script_title = models.CharField(max_length=50, verbose_name='Имя скрипта')
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children',
                            db_index=True, on_delete=models.CASCADE)
    is_chapter = models.BooleanField(default=False)
    total_rows = models.IntegerField(default=0)
    translated = models.IntegerField(default=0)
    edited_first_pass = models.IntegerField(default=0)
    edited_second_pass = models.IntegerField(default=0)
    last_update = models.DateTimeField(verbose_name='Дата последнего обновления',
                                       auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'statistics_chapter'

    def __str__(self):
        return self.script_title

    def delete(self):
        super(TranslationStatisticsChapter, self).delete()

    def recalculate(self):
        if self.is_chapter:
            all_counts = self.get_children().aggregate(
                total_rows_all=Sum('total_rows'),
                total_translated=Sum('translated'),
                total_edited_first_pass=Sum('edited_first_pass'),
                total_edited_second_pass=Sum('edited_second_pass'),
                last_updated=Max('last_update')
            )

            # Additional check for empty chapter, which has all "Sums" == None
            self.total_rows = all_counts['total_rows_all'] or 0
            self.translated = all_counts['total_translated'] or 0
            self.edited_first_pass = all_counts['total_edited_first_pass'] or 0
            self.edited_second_pass = all_counts['total_edited_second_pass'] or 0

            # Update last update for all parent chapters
            if all_counts['last_updated'] is not None and all_counts['last_updated'] > self.last_update:
                self.last_update = all_counts['last_updated']

            super(TranslationStatisticsChapter, self).save()

        if self.parent:
            self.parent.recalculate()
        elif self.lft == 1:
            TranslationStatistics.objects.filter(tree_id=self.tree_id).update(last_update=self.last_update)


class TranslationBetaLink(PublishModel):
    title = models.CharField(max_length=50, verbose_name="Название")
    url = models.CharField(max_length=200, verbose_name="URL")
    comment = models.TextField(max_length=2000, default='', blank=True, verbose_name="Комментарий")
    translation_item = models.ForeignKey('TranslationItem', on_delete=models.PROTECT, null=True, blank=True,
                                         verbose_name='Перевод')
    approved = models.BooleanField(verbose_name="Подтверждена", default=False)
    rejected = models.BooleanField(verbose_name="Отклонена", default=False)
    last_update = models.DateTimeField(verbose_name='Дата последнего обновления',
                                       auto_now_add=True, null=True, blank=True)

    class Meta:
        db_table = 'statistics_betalink'
        verbose_name = 'Ссылка на патч'
        verbose_name_plural = 'Ссылки на патчи'

    def __str__(self):
        return self.url

    def delete(self, force=False):
        if force:
            super(TranslationBetaLink, self).delete()
        else:
            self.is_published = False
            super(TranslationBetaLink, self).save()


class TranslationItem(PublishModel):
    visual_novel = models.ForeignKey(VisualNovel, on_delete=models.PROTECT, verbose_name='Визуальная новелла')
    statistics = models.ForeignKey(TranslationStatistics, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='Привязанная статистика')
    moderators = models.ManyToManyField(User, blank=True, verbose_name="Модераторы")
    subscriber = models.ManyToManyField(Profile, blank=True,
                                        verbose_name="Подписчики", through='TranslationSubscription')
    translator = models.ForeignKey(Translator, verbose_name='Переводчик', on_delete=models.PROTECT,
                                   null=True, blank=True)
    status = BitField(verbose_name='Битовый код статуса',
                        flags=(('active', 'Активный'), ('frozen', 'Замороженный'), ('onhold', 'Давно не обновлялся'),
                            ('finished', 'Завершен'), ('readytogo', 'Готовится к выпуску'), ('intest', 'Тестирование'),
                            ('dropped', 'Заброшен')
                        ),
                        default=TRANSLATION_ITEM_ACTIVE_BITCODE)

    class Meta:
        db_table = 'translation_items'
        verbose_name = 'Перевод'
        verbose_name_plural = 'Переводы'

    def __str__(self):
        return f'Перевод {self.visual_novel.title}'

    def get_absolute_url(self):
        return reverse('translation_item', kwargs={'vn_alias': self.visual_novel.alias})

    def save(self, *args, **kwargs):
        if not self.id:
            parental_translation_node = TranslationStatisticsChapter.objects.create(
                parent=None,
                title='Раздел самого высокого уровня',
                script_title='Раздел самого высокого уровня',
                is_chapter=True
            )
            translation_statistics, _ = TranslationStatistics.objects.get_or_create(
                tree_id=parental_translation_node.tree_id
            )
            self.statistics = translation_statistics
        super(TranslationItem, self).save(*args, **kwargs)

    def delete(self):
        tree_id = self.statistics.tree_id
        TranslationStatisticsChapter.objects.filter(tree_id=tree_id).delete()
        TranslationStatistics.objects.get(pk=self.statistics.pk).delete()
        super(TranslationItem, self).delete()

    def update_to_status(self, status_index):
        self.status = 2 ** status_index
        super(TranslationItem, self).save()

        if TRANSLATION_ITEMS_STATUSES[status_index][4]:
            # Update "last_update" for statistics
            statistics = TranslationStatistics.objects.get(id=self.statistics.id)
            statistics.last_update = arrow.utcnow().to(settings.TIME_ZONE).datetime
            statistics.save()


class TranslationSubscription(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Пользователь')
    translation = models.ForeignKey(TranslationItem, on_delete=models.CASCADE, verbose_name='Перевод',
                                    null=True, blank=True, related_name='translations_set')

    class Meta:
        db_table = 'translation_subscriptions'
        verbose_name = 'Подписка на рассылку'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return 'Подписка {} на рассылку статистики перевода {}'.format(
            self.profile.user.username, self.translation.visual_novel.title)


class TranslationItemSendToVK(models.Model):
    translation_item = models.ForeignKey(TranslationItem, verbose_name='Перевод', on_delete=models.CASCADE)
    vk_group_id = models.CharField(verbose_name='ID группы ВК', max_length=255, default='')
    post_date = models.DateField(verbose_name='Дата', auto_now_add=True)

    pictures_statistics = models.TextField(verbose_name='Статистика изображений', max_length=500, default='',
                                           blank=True)
    technical_statistics = models.TextField(verbose_name='Статистика тех. части', max_length=500, default='',
                                            blank=True)
    comment = models.TextField(verbose_name='Статистика изображений', max_length=2000, default='', blank=True)
    last_update = models.DateTimeField(verbose_name='Дата последнего обновления',
                                       null=True, blank=True)
    total_rows = models.IntegerField(default=0, verbose_name='Всего строк')
    translated = models.IntegerField(default=0, verbose_name='Переведено')
    edited_first_pass = models.IntegerField(default=0, verbose_name='Первый проход редактуры')
    edited_second_pass = models.IntegerField(default=0, verbose_name='Второй проход редактуры')
    status = models.IntegerField(default=1, verbose_name='Статус перевода')

    class Meta:
        db_table = 'translation_item_send_to_vk'
        verbose_name = 'Перевод отпраленный в группу ВК'
        verbose_name_plural = 'Переводы отпраленные в группы ВК'

    def __str__(self):
        return 'Перевод {} отправленный в ВК для группы {}'.format(
            self.translation_item.visual_novel.title, self.vk_group_id)

    @classmethod
    def create_from_translation_item(cls, translation_item, vk_group_id):
        ts = translation_item.statistics
        base_node = TranslationStatisticsChapter.objects.get(tree_id=ts.tree_id, lft=1, parent=None)
        return cls(
            translation_item=translation_item,
            vk_group_id=vk_group_id,
            pictures_statistics=ts.pictures_statistics,
            technical_statistics=ts.technical_statistics,
            comment=ts.comment,
            last_update=ts.last_update,
            total_rows=base_node.total_rows,
            translated=base_node.translated,
            edited_first_pass=base_node.edited_first_pass,
            edited_second_pass=base_node.edited_second_pass,
            status=translation_item.status.mask
        )


class TranslationBetaLinkSendToVK(models.Model):
    link = models.ForeignKey(TranslationBetaLink, verbose_name='Ссылка на патч', on_delete=models.CASCADE)
    vk_group_id = models.CharField(verbose_name='ID группы ВК', max_length=255, default='')
    post_date = models.DateField(verbose_name='Дата', auto_now_add=True)

    class Meta:
        db_table = 'translation_betalink_send_to_vk'
        verbose_name = 'Бетассылка, отправленная в группу ВК'
        verbose_name_plural = 'Бетассылки, отправленные в группы ВК'

    def __str__(self):
        return 'Ссылка {} отправленная в ВК для группы {}'.format(
            self.link.url, self.vk_group_id
        )
