from datetime import datetime, timezone
from django.shortcuts import render, get_object_or_404

from .models import Category, Post


def index(request):
    template_name = 'blog/index.html'

    posts = Post.objects.all().select_related('category').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(timezone.utc)
    )[:5]

    context = {'post_list': posts}
    return render(request, template_name, context)


def post_detail(request, post_id):
    template_name = 'blog/detail.html'

    post = get_object_or_404(
        Post,
        pk=post_id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(timezone.utc)
    )

    context = {'post': post}
    return render(request, template_name, context)


def category_posts(request, category_slug):
    template_name = 'blog/category.html'

    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    posts = category.posts.filter(
        is_published=True,
        pub_date__lte=datetime.now(timezone.utc)
    )

    context = {
        'category': category,
        'post_list': posts
    }
    return render(request, template_name, context)
