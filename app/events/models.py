from django.db import models
from django.contrib.auth.models import User




# Create your models here.

# These are the variables a user will have to create an event
class Event(models.Model):
    name = models.CharField(max_length=100)
    desc = models.TextField(null = True, blank = True)
    location = models.CharField(max_length=200)
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
	    return self.name
