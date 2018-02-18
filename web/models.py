from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=100)
    section = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/", blank=True)

    def __str__(self):
        return self.name

class SliderValues(models.Model):
    slider1 = models.IntegerField(default=0)
    slider2 = models.IntegerField(default=0)
    text = models.CharField(max_length=200, default='')