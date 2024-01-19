from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Count, QuerySet
from django.utils import timezone

ITEMS_PER_PAGE = 10


def filter_posts(
        post_objects: QuerySet,
        author=None
) -> QuerySet:
    filters = {}

    if not author:
        filters['is_published'] = True
        filters['category__is_published'] = True
        filters['pub_date__lte'] = get_current_date()

    return post_objects.select_related('category', 'author',
                                       'location').filter(**filters)


def get_current_date() -> datetime:
    return timezone.now()


def annotate_comment_count(posts: QuerySet) -> QuerySet:
    return posts.annotate(comment_count=Count('comments'))


def paginate_data(request, data, items_per_page=ITEMS_PER_PAGE):
    ordered_data = data.order_by('-pub_date')
    paginator = Paginator(ordered_data, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
