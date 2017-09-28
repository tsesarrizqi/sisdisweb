from django.db import models

# Create your models here.
class CountReq(models.Model):
    string = models.CharField(max_length=255, primary_key=True)
    count = models.IntegerField()
