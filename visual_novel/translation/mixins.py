from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from .models import TranslationItem, TranslationStatisticsChapter, TranslationBetaLink

from .errors import (
    TranslationNotFound, InvalidValueOnRowsQuantity, ParentDoesNotExist, InvalidMoveParent, InvalidBetaLinkUrl,
    BetaLinkUrlAlreadyExists, BetaLinkDoesNotExist, TranslationStatusDoesNotExist, TranslationCannotBeEditedDueToStatus,
    TranslationStatusCannotBeChangedToItself
)

from .utils import get_status_tuple_for_translation_item


class TranslationExistsValidator:
    def validate_translation_exists(self, translation_item_id):
        try:
            return TranslationItem.objects.get(
                id=translation_item_id,
                visual_novel__is_published=True,
                is_published=True
            )
        except TranslationItem.DoesNotExist:
            raise TranslationNotFound()


class TranslationChapterExistsValidator:
    def validate_chapter_exists(self, chapter_id, translation_item):
        try:
            chapter = TranslationStatisticsChapter.objects.get(
                id=chapter_id,
                tree_id=translation_item.statistics.tree_id
            )
            return chapter
        except TranslationStatisticsChapter.DoesNotExist:
            raise TranslationNotFound()


class InputNumberValidator:
    def validate_numbers_input(self, total, translated, edited_first, edited_second, is_chapter):

        # Quantities of rows for chapters are recalculated outside the command
        if is_chapter:
            return

        ttl = int(total)
        trl = int(translated)
        edf = int(edited_first)
        eds = int(edited_second)

        # Validate rows' numbers consistency
        if (trl > ttl) or (edf > trl) or (eds > edf):
            raise InvalidValueOnRowsQuantity()

        return


class ParentExistsValidator:
    def validate_parent_section_exists(self, translation_item, parent_id, move_to):
        parent_id = None if not parent_id else parent_id
        try:
            parent = TranslationStatisticsChapter.objects.get(
                id=parent_id,
                tree_id=translation_item.statistics.tree_id
            )
        except TranslationStatisticsChapter.DoesNotExist:
            raise ParentDoesNotExist()
        if (not parent.is_chapter) and (move_to in ['first-child', 'last-child']):
            raise InvalidMoveParent()
        return parent


class BetaLinkUrlValidator:
    def validate_betalink_url(self, url):
        try:
            URLValidator()(url)
        except ValidationError:
            raise InvalidBetaLinkUrl()


class BetaLinkUrlUniqueValidator:
    def validate_betalink_url_unique(self, id, url):
        if TranslationBetaLink.objects.filter(
            url=url,
            is_published=True
        ).exclude(id=id).exists():
            raise BetaLinkUrlAlreadyExists()


class BetaLinkExistsValidator:
    def validate_betalink_exists(self, id):
        try:
            return TranslationBetaLink.objects.get(id=id)
        except TranslationBetaLink.DoesNotExist:
            raise BetaLinkDoesNotExist()


class TranslationStatusExistsValidator:
    def validate_translation_status_exists(self, status):
        try:
            return list(TranslationItem.status).index(status)
        except ValueError:
            raise TranslationStatusDoesNotExist()


class TranslationCanBeEditedValidator:
    def validate_translation_can_be_edited(self, translation_item):
        status_tuple = get_status_tuple_for_translation_item(translation_item)
        if not status_tuple[6]:
            raise TranslationCannotBeEditedDueToStatus()


class StatusIsNotTheSameValidator:
    def validate_status_is_not_the_same(self, translation_item, status_index):
        if translation_item.status.mask == 2 ** status_index:
            raise TranslationStatusCannotBeChangedToItself()
