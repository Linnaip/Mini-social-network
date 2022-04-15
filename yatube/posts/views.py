from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings as s
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Group, Post


User = get_user_model()


def index(request):
    """Главная страница."""
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, s.CONSTANT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'post_list': posts_list,
        'paginator': paginator
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, s.CONSTANT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    count_list = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, s.CONSTANT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'count_list': count_list
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    context = {
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile')
    return render(request, 'posts/create_post.html', {'form': form})
