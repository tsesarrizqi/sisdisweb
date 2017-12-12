from django.db import models

# Create your models here.
class CountReq(models.Model):
    string = models.CharField(max_length=255, primary_key=True)
    count = models.IntegerField()

class Nasabah(models.Model):
	user_id = models.CharField(max_length=10,primary_key=True)
	name = models.CharField(max_length=255)
	saldo = models.IntegerField()

class Ping(models.Model):
	npm = models.CharField(max_length=10,primary_key=True)
	date = models.DateTimeField()
