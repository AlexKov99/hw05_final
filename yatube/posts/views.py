from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm
from .utils import paginator


def index(request):
    posts = Post.objects.all()
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related(
        'group').filter(group=group)
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author').filter(author=author)
    page_obj = paginator(request, posts)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        print(form)
        post_create = form.save(commit=False)
        post_create.author = request.user
        post_create.save()
        return redirect('posts:profile', request.user)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post,
                    data=request.POST or None,
                    files=request.FILES or None,)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': is_edit,
                                                      'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user).all()
    page_obj = paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    follow_user = request.user
    if follow_user != author:
        Follow.objects.get_or_create(
            author=author,
            user=follow_user,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    follow_user = request.user
    if follow_user != author:
        Follow.objects.get(
            author=author,
            user=follow_user,
        ).delete()
    return redirect('posts:follow_index')
