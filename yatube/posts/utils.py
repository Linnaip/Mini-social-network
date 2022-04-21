from django.conf import settings as s
from django.core.paginator import Paginator


def get_page_context(request, posts_list):
    """Код работы пагинатора."""
    paginator = Paginator(posts_list, s.CONSTANT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
