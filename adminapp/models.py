from django.db import models

# Create your models here.
class Datasets_Details(models.Model):
    dataset_id = models.AutoField(primary_key = True)
    dataset_name = models.FileField(null=True)
    file_size = models.CharField(max_length = 100) 
    formated_file_size = models.CharField(max_length= 100, null=True)
    date_time = models.DateTimeField(auto_now = True)
    
    class Meta:
        db_table = 'datasets_details'
        ordering = ['-dataset_id']

class Random_Forest(models.Model):
    S_No = models.AutoField(primary_key=True)
    Accuracy = models.TextField(max_length=100)
    Result = models.TextField(max_length=100)

    class Meta:
        db_table = 'random_forest'

