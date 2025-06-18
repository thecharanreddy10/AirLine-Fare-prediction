from django.db import models
from mainapp.models import *

# Create your models here.
class Feedback(models.Model):
    Feed_id = models.AutoField(primary_key=True)
    Rating=models.CharField(max_length=100,null=True)
    Review=models.CharField(max_length=225,null=True)
    Sentiment=models.CharField(max_length=100,null=True)
    Reviewer=models.ForeignKey(UserDetails, on_delete=models.CASCADE,null=True)
    datetime=models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feedback_details'
