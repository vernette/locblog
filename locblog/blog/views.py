from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post
from .utils import (annotate_comment_count, filter_posts, get_current_date,
                    paginate_data)


def index(request):
    posts = filter_posts(
        annotate_comment_count(Post.objects)
    )

    return render(
        request,
        template_name='blog/index.html',
        context={
            'page_obj': paginate_data(request, posts),
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_category = post.category

    if (
            (
                not post.is_published
                or post.pub_date > get_current_date()
                or not post_category.is_published
            )
            and post.author != request.user
    ):
        raise Http404()

    form = CommentForm()
    comments = post.comments.select_related('author').all()

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
        Category,
        slug=category_slug,
        is_published=True
    )

    posts_by_category = filter_posts(
        annotate_comment_count(category.posts)
    )

    return render(
        request,
        template_name='blog/category.html',
        context={
            'category': category,
            'page_obj': paginate_data(
                request, posts_by_category
            ),
        }
    )


def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    author = user if request.user == user else None

    user_posts = filter_posts(
        annotate_comment_count(user.posts),
        author=author
    )

    return render(
        request,
        template_name='blog/profile.html',
        context={
            'profile': user,
            'page_obj': paginate_data(
                request,
                user_posts
            )
        }
    )


@login_required
def post_create_or_edit(request, post_id=None):
    post = None
    if post_id:
        post = get_object_or_404(Post, id=post_id)
        if request.user != post.author:
            return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        if post_id:
            return redirect('blog:post_detail', post_id=post_id)
        return redirect('blog:profile', username=request.user.username)

    return render(
        request,
        template_name='blog/create.html',
        context={
            'form': form
        }
    )


def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        raise PermissionDenied()

    form = PostForm(instance=post)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(
        request,
        template_name='blog/create.html',
        context={
            'form': form
        }
    )


@login_required
def edit_profile(request):
    user = request.user

    form = ProfileForm(request.POST or None, instance=user)

    if form.is_valid():
        form.save()

    return render(
        request,
        template_name='blog/user.html',
        context={
            'form': form
        }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(
        to='blog:post_detail',
        post_id=post_id
    )


@login_required()
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)

    if request.user != comment.author:
        raise PermissionDenied()

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(
        request,
        template_name='blog/comment.html',
        context={
            'form': form,
            'comment': comment
        }
    )


@login_required()
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)

    if request.user != comment.author:
        raise PermissionDenied()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(
        request,
        template_name='blog/comment.html',
        context={
            'comment': comment
        }
    )
