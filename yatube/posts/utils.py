from django.core.paginator import Paginator

from yatube.settings import AMOUNT


def paginator(request, post_list):
    paginator_utils = Paginator(post_list, AMOUNT)
    page_number = request.GET.get('page')
    return paginator_utils.get_page(page_number)
