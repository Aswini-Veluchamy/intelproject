from django.db import models
from django_quill.fields import QuillField

# Create your models here.


class KeyMessage(models.Model):
    ''' created database fields'''
    body = QuillField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "key_message"

class KeyMessageTable(models.Model):
    ''' created database fields'''
    message = models.CharField(max_length=200)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "key_message_table"

class RiskTable(models.Model):
    ''' created database fields'''
    problem_statement = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    comments = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.message

    class Meta:
        db_table = "risk_table"