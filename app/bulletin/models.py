from django.conf import settings
from django.db import models


class Announcement(models.Model):
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=3000)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self):
        return self.title
