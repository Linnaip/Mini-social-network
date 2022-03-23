from django.conf import settings as s
from django.shortcuts import render, get_object_or_404

from .models import Group, Post


def index(request):
    """Главная страница."""
    posts = Post.objects.all()[:s.CONSTANT]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница с инфорацией о Post."""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()[:s.CONSTANT]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
