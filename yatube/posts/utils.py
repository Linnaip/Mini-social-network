from django.conf import settings as s
from django.core.paginator import Paginator


def get_page_context(posts_list):
    """Код работы пагинатора."""
    paginator = Paginator(posts_list, s.CONSTANT)
    return paginator
