from datetime import datetime

from django.db.models import Count, QuerySet
from django.utils import timezone


def filter_posts(
        post_objects: QuerySet,
        author=None,
        location=None
) -> QuerySet:
    filters = {}

    if author:
        filters['author'] = author
    else:
        filters['is_published'] = True
        filters['category__is_published'] = True
        filters['pub_date__lte'] = get_current_date()

    if location:
        filters['location'] = location

    return post_objects.select_related('category', 'author',
                                       'location').filter(**filters)


def get_current_date() -> datetime:
    return timezone.now()


def annotate_comment_count(posts: QuerySet) -> QuerySet:
    return posts.annotate(comment_count=Count('comments'))
