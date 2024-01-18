from django.utils import timezone
from django.db.models import Count
from django.db.models import QuerySet
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .models import Post, Category, Comment
from .forms import PostForm, ProfileForm, CommentForm


def filter_posts(post_objects: QuerySet) -> QuerySet:
    return post_objects.select_related('category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def paginate_data(request, data, items_per_page=10):
    ordered_data = data.order_by('-pub_date')
    paginator = Paginator(ordered_data, items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = filter_posts(
        Post.objects.annotate(
            comment_count=Count('comments')
        )
    )

    return render(
        request,
        template_name='blog/index.html',
        context={
            'page_obj': paginate_data(request, posts),
        }
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_category = post.category

    if not post.is_published and post.author != request.user:
        raise Http404()

    if post.pub_date > timezone.now() and post.author != request.user:
        raise Http404()

    if not post_category.is_published and post.author != request.user:
        raise Http404()

    if request.method == 'GET':
        form = CommentForm()
    else:
        form = None

    comments = post.comments.all()

    return render(
        request,
        template_name='blog/detail.html',
        context={
            'post': post,
            'form': form,
            'comments': comments
        },
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        klass=Category,
        slug=category_slug,
        is_published=True
    )

    posts_by_category = filter_posts(
        category.posts.annotate(
            comment_count=Count('comments')
        )
    )

    context = {
        'category': category,
        'page_obj': paginate_data(request, posts_by_category),
    }

    return render(
        request,
        template_name='blog/category.html',
        context=context
    )


def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if request.user == user:
        user_posts = user.post_set.annotate(
            comment_count=Count('comments')
        )
    else:
        user_posts = user.post_set.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        )

    context = {
        'profile': user,
        'page_obj': paginate_data(
            request,
            user_posts
        )
    }

    return render(
        request,
        template_name='blog/profile.html',
        context=context
    )


@login_required
def post_create_or_edit(request, post_id=None):
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        if request.user != post.author:
            return HttpResponseRedirect(f'/posts/{post_id}/')
    else:
        post = None

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if post_id:
                return redirect('blog:post_detail', post_id=post_id)
            else:
                return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form, 'post': post})


def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        raise PermissionDenied()

    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if request.user != user:
        raise PermissionDenied()

    form = ProfileForm(request.POST or None, instance=user)

    context = {'form': form}

    if form.is_valid():
        form.save()

    return render(
        request,
        template_name='blog/user.html',
        context=context
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('blog:post_detail', post_id=post_id)

    return redirect('blog:post_detail', post_id=post_id)


@login_required()
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if request.user != comment.author:
        raise PermissionDenied()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html',
                  {'form': form, 'post': post, 'comment': comment})


@login_required()
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user != comment.author:
        raise PermissionDenied()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html',
                  {'post': post, 'comment': comment})
