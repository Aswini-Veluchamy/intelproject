from django import forms
from .models import KeyMessage


class PostForm(forms.ModelForm):
   class Meta:
      model = KeyMessage
      fields = ['message', 'body']