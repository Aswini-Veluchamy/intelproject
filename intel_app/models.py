from django.db import models
from django_quill.fields import QuillField
from datetime import datetime

# Create your models here.


class KeyMessage(models.Model):
    '''  created database fields '''
    body = QuillField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.created_at

    class Meta:
        db_table = "key_message"


class KeyMessageTable(models.Model):
    ''' created database fields'''
    message_id = models.CharField(max_length=128)
    message = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    project = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "key_message_table"


class RiskTable(models.Model):
    ''' created database fields'''
    problem_statement = models.CharField(max_length=250, default='problem_statement')
    status = models.CharField(max_length=200, default='status')
    owner = models.CharField(max_length=200, default='owner')
    message = models.CharField(max_length=250, default='message')
    eta = models.DateTimeField(default=datetime.now())
    risk = models.DateTimeField(default=datetime.now())
    severity = models.CharField(max_length=200, default='severity')
    impact = models.CharField(max_length=200, default='impact')
    risk_id = models.CharField(max_length=100, default='risk_id')
    project = models.CharField(max_length=200, default='project')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner

    class Meta:
        db_table = "risk_table"
