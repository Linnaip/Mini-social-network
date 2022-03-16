from django.shortcuts import render
from django.http import HttpResponse
from .models import Post


# Create your views here.


def index(request):
    """Главная страница."""
    posts = Post.objects.order_by('-pub_date')[:10]
    # В словаре context отправляем информацию в шаблон
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница с инфорацией о Post."""
    template = 'posts/group_posts.html'
    title = 'Лев Толстой – зеркало русской революции.'
    context = {
        'title': title
    }
    return HttpResponse(request, slug, template, context)
