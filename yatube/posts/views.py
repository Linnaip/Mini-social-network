from django.core.paginator import Paginator
from django.conf import settings as s
from django.shortcuts import render, get_object_or_404

from .models import Group, Post


def index(request):
    """Главная страница."""
    posts_list = Post.objects.all()[:s.CONSTANT]
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
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
