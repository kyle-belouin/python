from django.db import models
from django.forms import ModelForm
from model_utils.models import TimeStampedModel

# https://docs.djangoproject.com/en/4.0/ref/models/fields/


class SpotiStats(models.Model):
    client_id = models.CharField(max_length=50)
    secret = models.CharField(max_length=50)
