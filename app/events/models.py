from django.db import models

# Create your models here.
class event(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField(max_length=200)
    location = models.CharField(max_length=200)
    time = models.CharField(max_length=10)

def __str__(self):
	return self.title