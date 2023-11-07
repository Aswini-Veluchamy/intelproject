from django.db import models
from datetime import datetime

# Create your models here.


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
    user = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.owner

    class Meta:
        db_table = "risk_table"


class KeyProgramMetricTable(models.Model):
    ''' created database fields'''
    category = models.CharField(max_length=250, default='category')
    metric = models.CharField(max_length=200, default='metric')
    fv_target = models.CharField(max_length=250, default='fv_target')
    current_week_actual = models.CharField(max_length=200, default='current_week_actual')
    current_week_plan = models.CharField(max_length=200, default='current_week_plan')
    status = models.CharField(max_length=200, default='status')
    comments = models.CharField(max_length=250, default='comments')
    metric_id = models.CharField(max_length=100, default='metric_id')
    project = models.CharField(max_length=200, default='project')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.category

    class Meta:
        db_table = "key_program_metric_table"


class DetailsMessageTable(models.Model):
    ''' created database fields'''
    details_id = models.CharField(max_length=128, default='details_id')
    message = models.CharField(max_length=200, default='message')
    user = models.CharField(max_length=200, default='user')
    project = models.CharField(max_length=200, default='project')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "details_message_table"
