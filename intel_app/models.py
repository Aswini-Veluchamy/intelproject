from django.db import models
from datetime import datetime
from django_mysql.models import ListCharField, ListTextField

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
    status = ListCharField(
        base_field=models.CharField(max_length=10),
        size=6,
        max_length=(6 * 11)
    )
    owner = models.CharField(max_length=200, default='owner')
    message = models.CharField(max_length=250, default='message')
    eta = models.DateTimeField(default=datetime.now())
    risk = models.DateTimeField(default=datetime.now())
    severity = ListTextField(
        base_field=models.CharField(max_length=10),
        size=100,
    )
    impact = ListCharField(
        base_field=models.CharField(max_length=10),
        size=6,
        max_length=(6 * 11)
    )
    risk_id = models.CharField(max_length=100, default='risk_id')
    project = models.CharField(max_length=100, default='project')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, default='user')
    display = models.CharField(max_length=100, default='false')

    def __str__(self):
        return self.owner

    class Meta:
        db_table = "risk_table"


class KeyProgramMetricTable(models.Model):
    ''' created database fields'''
    metric = models.CharField(max_length=200, default='metric')
    fv_target = models.CharField(max_length=250, default='fv_target')
    current_week_actual = models.CharField(max_length=200, default='current_week_actual')
    current_week_plan = models.CharField(max_length=200, default='current_week_plan')
    status = ListCharField(
        base_field=models.CharField(max_length=10),
        size=6,
        max_length=(6 * 11)
    )
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


class ScheduleMetricTable(models.Model):
    ''' created database fields'''
    milestone = models.CharField(max_length=250, default='milestone')
    por_commit = models.DateTimeField(default='por_commit')
    por_trend = models.DateTimeField(default='por_trend')
    status = ListCharField(
        base_field=models.CharField(max_length=10),
        size=6,
        max_length=(6 * 11)
    )
    comments = models.CharField(max_length=200, default='comments')
    schedule_id = models.CharField(max_length=100, default='schedule_id')
    project = models.CharField(max_length=200, default='project')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.milestone

    class Meta:
        db_table = "schedule_table"


class LinksMetricTable(models.Model):
    ''' created database fields'''
    list = models.CharField(max_length=250, default='list')
    link = models.URLField(max_length=200)
    links_id = models.CharField(max_length=100, default='links_id')
    project = models.CharField(max_length=200, default='project')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, default='user')

    def __str__(self):
        return self.link

    class Meta:
        db_table = "links_table"
