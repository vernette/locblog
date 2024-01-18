from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)


class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )


class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'cols': 10,
                'rows': 5,
                'placeholder': 'Введите ваш комментарий...'
            }
        ),
        label='Текст комментария'
    )

    class Meta:
        model = Comment
        fields = ('text',)
