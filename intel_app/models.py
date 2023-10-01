from django.db import models

# Create your models here.


class KeyMessage(models.Model):
    ''' created database fields'''
    message = models.CharField(max_length=200)

    def __str__(self):
        return self.message

    class Meta:
        db_table = "key_message"
