from django.db import models

# Create your models here.
class Departments(models.Model):
  name = models.CharField(max_length=255)
  code = models.CharField(max_length=255)

class Courses(models.Model):
  fid = models.IntegerField()
  name = models.CharField(max_length=255)
  code = models.CharField(max_length=255)

class Teachers(models.Model):
  name = models.CharField(max_length=255)
  code = models.CharField(max_length=255)