import shutil
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, Comment
from .const_test import (CONST_TEXT, CONST_TEXT_EDIT,
                         CONST_GROUP_1, CONST_SLUG_1,
                         CONST_DESCRIPTION_1, CONST_GROUP_2,
                         CONST_SLUG_2, CONST_DESCRIPTION_2,
                         TEMP_MEDIA_ROOT)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_1,
        )

        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создаёт новую запись"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        form_data = {
            'text': CONST_TEXT,
            'group': self.group.id,
            'image': uploaded,
        }
        post_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        last_post = Post.objects.order_by('-pub_date').last()
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.text, CONST_TEXT)
        self.assertEqual(last_post.image, uploaded)

    def test_edit_post(self):
        """Валидная форма редактирует существующую запись"""
        post = Post.objects.create(
            author=self.user,
            group=self.group
        )
        group2 = Group.objects.create(
            title=CONST_GROUP_2,
            slug=CONST_SLUG_2,
            description=CONST_DESCRIPTION_2
        )

        form_data = {
            'group': group2.id,
            'text': CONST_TEXT_EDIT,
        }

        self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            post.pk}), data=form_data, follow=True)
        edit_post = Post.objects.get(pk=post.pk)
        self.assertEqual(
            edit_post.text, CONST_TEXT_EDIT)
        self.assertEqual(
            edit_post.group.id, group2.id)
        self.assertEqual(
            edit_post.author, self.user)

    def test_add_comment(self):
        post = Post.objects.create(

            author=self.user,
            group=self.group
        )

        form_data = {
            'text': CONST_TEXT,
        }
        comments_count = Comment.objects.count()
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': post.pk}),
            data=form_data,
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(Comment.objects.filter(
            author=self.user,
            text=CONST_TEXT,
            post=post).exists())
