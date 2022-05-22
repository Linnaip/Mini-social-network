from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Comment, User, Follow
from .utils import get_page_context


@cache_page(4*5)
def index(request):
    """Главная страница."""
    posts_list = Post.objects.all()
    page_obj = get_page_context(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводит шаблон с группами постов."""
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    page_obj = get_page_context(request, posts_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Выводит шаблон профайла пользователя."""
    author = get_object_or_404(User, username=username)
    posts_list = Post.objects.filter(author=author).order_by('-pub_date')
    count_list = Post.objects.filter(author=author).count()
    page_obj = get_page_context(request, posts_list)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False
    context = {
        'author': author,
        'page_obj': page_obj,
        'count_list': count_list,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводит шаблон поста пользователя."""
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    count_list = Post.objects.filter(author=author).count()
    comments = Comment.objects.filter(post=post).all()
    form = CommentForm()
    context = {
        'author': author,
        'post': post,
        'count_list': count_list,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Выводит шаблон создания поста."""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Выводит шаблон редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    context = {
        'form': form,
        'post': post,
    }
    if request.method == 'GET':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id=post.id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page_context(request, posts_list)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(author=author, user=user)
    if user.is_authenticated != author:
        if not follower:
            Follow.objects.create(author=author, user=user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(author=author, user=user)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username)
