from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post
from .const_test import (CONST_GROUP_1, CONST_SLUG_1,
                         CONST_DESCRIPTION_1, CONST_TEXT)
from yatube.settings import CONST_NUMB_CHARS

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_1,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=CONST_TEXT,
        )

    def test_models_have_correct_object_names_post(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:CONST_NUMB_CHARS]
        self.assertEqual(expected_object_name, str(post))

    def test_models_have_correct_object_names_group(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
