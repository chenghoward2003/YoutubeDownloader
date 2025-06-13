from django.db import models
from django.core.files import File
from django.contrib.auth.models import User
import uuid

class Content(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=255, default="")
    cover = models.ImageField(upload_to='content_covers/')
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title