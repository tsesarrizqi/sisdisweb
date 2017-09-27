from django.db import models

# Create your models here.
class CountReq(models.Model):
    string = models.CharField(primary_key=True)
    count = models.IntegerField()
