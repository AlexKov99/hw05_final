import shutil

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..models import Group, Post, Follow
from ..forms import PostForm
from yatube.settings import AMOUNT
from .const_test import (CONST_TEXT, CONST_GROUP_1,
                         CONST_SLUG_1, CONST_DESCRIPTION_1,
                         CONST_GROUP_2, CONST_SLUG_2,
                         CONST_DESCRIPTION_2, TEMP_MEDIA_ROOT)


User = get_user_model()

TEST_CONST: int = AMOUNT + 3


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class StaticViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_1,
        )
        cls.group_2 = Group.objects.create(
            title=CONST_GROUP_2,
            slug=CONST_SLUG_2,
            description=CONST_DESCRIPTION_2
        )

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

        cls.post = Post.objects.create(
            author=cls.user,
            text=CONST_TEXT,
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group_posts',
                    kwargs={'slug':
                            self.group.slug}): 'posts/group_list.html', }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context(response)

    def check_context(self, response):
        response_post = response.context['page_obj'][0]
        posts_author = response_post.author
        posts_group = response_post.group
        posts_text = response_post.text
        posts_id = response_post.id
        post_image = response_post.image
        self.assertEqual(posts_author, self.post.author)
        self.assertEqual(posts_text, self.post.text)
        self.assertEqual(posts_group, self.group)
        self.assertEqual(posts_id, self.post.id)
        self.assertEqual(post_image, self.post.image)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_context(response)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug':
                                                      self.group.slug}))
        response_group = response.context.get('group').slug
        self.assertEqual(response_group, self.group.slug)
        self.check_context(response)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id':
                                                      self.post.id}))
        response_post = response.context.get('post')
        post_author = response_post.author
        post_group = response_post.group
        post_text = response_post.text

        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_text, self.post.text)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={
                    'username':
                    self.post.author.username}
            ))
        response_author = response.context.get('author').username
        self.assertEqual(response_author, self.post.author.username)
        self.check_context(response)

    def test_create_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, None)
        self.assertIsInstance(form, PostForm)

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id':
                                                              self.post.id}))
        form = response.context.get('form')
        response_post = response.context.get('post')
        post_author = response_post.author
        post_text = response_post.text
        is_edit = response.context.get('is_edit')
        self.assertEqual(is_edit, True)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_text, self.post.text)
        self.assertIsInstance(form, PostForm)

    def test_new_post_is_not_in_wrong_group_list(self):
        """Проверка, что пост не попал в другую группу"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug':
                                                 self.group_2.slug}))
        self.assertEqual(len(response.context.get('page_obj').object_list), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_2,
        )

        obj = (Post(author=cls.user,
                    text=f'Test {i}',
                    group=cls.group, ) for i in range(TEST_CONST))
        cls.posts = Post.objects.bulk_create(obj)
        for cls.post in cls.posts:
            return cls.post

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        url_names = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author.username}),
            reverse('posts:group_posts',
                    kwargs={'slug':
                            self.group.slug}), ]
        for url in url_names:
            with self.subTest():
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 AMOUNT)

    def test_second_page_contains_three_records(self):
        url_names = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author.username}),
            reverse('posts:group_posts',
                    kwargs={'slug':
                            self.group.slug}), ]
        for url in url_names:
            with self.subTest():
                response = self.client.get(url + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 TEST_CONST - AMOUNT)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='One')
        cls.user_2 = User.objects.create_user(username='Two')
        cls.user_3 = User.objects.create_user(username='Three')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_1,
        )
        cls.post1 = Post.objects.create(
            author=cls.user_1,
            text=CONST_TEXT,
            group=cls.group
        )
        cls.post2 = Post.objects.create(
            author=cls.user_2,
            text=CONST_TEXT,
            group=cls.group
        )
        cls.post3 = Post.objects.create(
            author=cls.user_3,
            text=CONST_TEXT,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)

    def test_authorized_can_follow(self):
        count_follow_before_follow = Follow.objects.count()
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', args={f'{self.user_2.username}'}))
        count_follow_after_follow = Follow.objects.count()
        self.assertRedirects(response, '/follow/')
        self.assertEqual(
            count_follow_after_follow, count_follow_before_follow + 1)
        self.assertEqual(Follow.objects.filter(user=self.user_1,
                                               author=self.user_2).exists(),
                         True)

    def test_authorized_can_unfollow(self):
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', args={f'{self.user_2.username}'}))
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', args={f'{self.user_2.username}'}))
        self.assertRedirects(response, '/follow/')
        self.assertEqual(Follow.objects.filter(user=self.user_1,
                                               author=self.user_2).exists(),
                         False)

    def test_post_in_follow(self):
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        count_before_follow = len(response.context.get('page_obj'))
        Follow.objects.get_or_create(user=self.user_1,
                                     author=self.user_2)
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        count_after_follow = len(response.context.get('page_obj'))
        self.assertEqual(count_before_follow + 1, count_after_follow)

    def test_post_in_unfollow(self):
        self.authorized_client.force_login(self.user_3)
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        count_posts_in_unfollow_user = len(response.context.get('page_obj'))
        self.assertEqual(count_posts_in_unfollow_user, 0)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title=CONST_GROUP_1,
            slug=CONST_SLUG_1,
            description=CONST_DESCRIPTION_1,)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        Post.objects.create(
            author=self.user,
            text=CONST_TEXT,
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:index'))
        cached_content = response.content
        Post.objects.last().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, cached_content)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cached_content)
