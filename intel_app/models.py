from django.db import models
from django_quill.fields import QuillField

# Create your models here.


class KeyMessage(models.Model):
    ''' created database fields'''
    message = models.CharField(max_length=200)
    body = QuillField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "key_message"
