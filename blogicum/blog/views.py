from datetime import datetime, timezone

from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404, resolve_url, redirect
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    UpdateView, CreateView, DeleteView, DetailView,
    ListView, TemplateView, RedirectView
)
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Category, Comment, Post, User
from .forms import ProfileForm, CommentForm, PostForm


@method_decorator(login_required, name='dispatch')
class YourProfile(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return resolve_url('blog:profile', get_user(self.request).username)


class Profile(TemplateView):
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cur_user = get_user(self.request)
        username = self.kwargs.get('username') or cur_user.username

        if cur_user.username == username:
            user = cur_user
            posts = user.posts.all().prefetch_related(
                'author',
                'category',
                'location',
                'comments'
            )
        else:
            user = get_object_or_404(User, username=username)
            posts = user.posts.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=datetime.now(timezone.utc)
            ).prefetch_related(
                'author',
                'category',
                'location',
                'comments'
            )

        page = Paginator(posts, 10).get_page(self.request.GET.get("page"))

        context.update(
            profile=user,
            page_obj=page
        )
        return context


@method_decorator(login_required, name='dispatch')
class EditProfile(UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileForm
    success_url = '/profile/'

    def get_object(self, queryset=None):
        return get_user(self.request)


class Index(ListView):
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.objects.all().filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.now(timezone.utc)
    ).prefetch_related(
        'author',
        'category',
        'location',
        'comments'
    )


class CategoryPosts(DetailView):
    template_name = 'blog/category.html'
    model = Category
    slug_url_kwarg = 'category_slug'
    context_object_name = 'category'
    queryset = Category.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.filter(
            is_published=True,
            pub_date__lte=datetime.now(timezone.utc)
        ).prefetch_related(
            'author',
            'category',
            'location',
            'comments'
        )
        page = Paginator(posts, 10).get_page(self.request.GET.get("page"))
        context['page_obj'] = page
        return context


@method_decorator(login_required, name='dispatch')
class CreateComment(CreateView):
    form_class = CommentForm
    success_url = '../'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author = get_user(self.request)
        comment.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment.save()
        return HttpResponseRedirect(self.success_url)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(('POST',))


@method_decorator(login_required, name='dispatch')
class EditComment(UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    success_url = '../../'

    def get_queryset(self):
        return super().get_queryset().filter(
            post=get_object_or_404(Post, pk=self.kwargs['post_id'])
        )

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != get_user(self.request):
            raise PermissionDenied
        return comment


@method_decorator(login_required, name='dispatch')
class DeleteComment(DeleteView):
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'comment_id'
    context_object_name = 'comment'
    success_url = '../../'

    def get_context_data(self, **kwargs):
        return {'comment': self.get_object()}

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != get_user(self.request):
            raise PermissionDenied
        return comment


class PostDetail(DetailView):
    template_name = 'blog/detail.html'
    model = Post
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'
    queryset = Post.objects.all().prefetch_related('comments')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author == get_user(self.request) or\
                obj.is_published and \
                obj.category.is_published and \
                obj.pub_date <= datetime.now(timezone.utc):
            return obj
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = CommentForm()
        comments = context['post'].comments.all().prefetch_related('author')

        context.update(
            form=form,
            comments=comments
        )
        return context


@method_decorator(login_required, name='dispatch')
class CreatePost(CreateView):
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = '/profile/'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['pub_date'].required = False
        return form

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = get_user(self.request)
        if post.pub_date is None:
            post.pub_date = datetime.now(timezone.utc)
        post.save()
        return HttpResponseRedirect(self.success_url)


class EditPost(UpdateView):
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    success_url = '../'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != get_user(self.request):
            raise PermissionDenied
        return obj

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except PermissionDenied:
            return redirect('blog:post_detail', self.kwargs['post_id'])

    def dispatch(self, request, *args, **kwargs):
        if get_user(request).is_anonymous:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class DeletePost(DeleteView):
    template_name = 'blog/create.html'
    model = Post
    pk_url_kwarg = 'post_id'
    success_url = '/profile/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != get_user(self.request):
            raise PermissionDenied
        return obj
