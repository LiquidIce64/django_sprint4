from django.forms import ModelForm

from .models import Comment, Post, User


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email'
        )


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'image',
            'pub_date',
            'location',
            'category'
        )
