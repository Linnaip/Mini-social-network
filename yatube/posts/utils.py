from django.core.paginator import Paginator
from django.conf import settings as s


# Код работы с пагинатором
def get_page_context(posts_list):
    paginator = Paginator(posts_list, s.CONSTANT)
    return paginator
