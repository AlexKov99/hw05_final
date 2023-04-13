import tempfile

from django.conf import settings


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
CONST_TEXT = 'Текстовый текст'
CONST_TEXT_EDIT = 'Изменённый текст текстового поста'
CONST_GROUP_1 = 'Тестовая группа'
CONST_SLUG_1 = 'test-slug'
CONST_DESCRIPTION_1 = 'Тестовое описание'
CONST_GROUP_2 = 'Тестовая группа 2'
CONST_SLUG_2 = 'test-slug2'
CONST_DESCRIPTION_2 = 'Тестовое описание 2'
