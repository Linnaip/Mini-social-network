from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import PostForm
from .models import Group, Post, User
from .utils import get_page_context


def index(request):
    """Главная страница."""
    posts_list = Post.objects.all()
    paginator = get_page_context(posts_list)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Выводит шаблон с группами постов."""
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = get_page_context(posts_list)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
    paginator = get_page_context(posts_list)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'count_list': count_list
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Выводит шаблон поста пользователя."""
    post = get_object_or_404(Post, id=post_id)
    request_user = request.user
    author = post.author
    count_list = Post.objects.filter(author=author).count()
    context = {
        'author': author,
        'post': post,
        'count_list': count_list,
        'request_user': request_user,
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
    form = PostForm(request.POST or None, instance=post)
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
