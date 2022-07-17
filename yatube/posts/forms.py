from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widgets = {
            'text': forms.Textarea
        }
        help_texts = {
            'text': 'Поле для текста',
            'group': 'Группа, к которой будет относиться пост'
        }
        empty_labels = {
            'group': 'Без группы'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
