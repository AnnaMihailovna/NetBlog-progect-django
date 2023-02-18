from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {'text': {'required': 'Поле не должно быть пустым'}}
        widgets = {'text': forms.Textarea}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
