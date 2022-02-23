from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    """Главная страница."""
    return HttpResponse('Главная страница')


def group_posts(request, slug):
    """Страница с инфорацией о Вайфу."""
    return HttpResponse(f'Лучшая вайфу:{slug}')