from django.forms import ModelForm
from django import forms

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        help_texts = {'text': 'Напишите что-нибудь интересное',
                      'group': 'По желанию можете выбрать группу'}
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение', }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария', }
