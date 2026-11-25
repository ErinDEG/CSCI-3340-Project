from urllib.parse import urlencode

from django.conf import settings
from django.db import models


class Event(models.Model):
    class Category(models.TextChoices):
        ACADEMIC = "academic", "Academic"
        SPORTS = "sports", "Sports"
        CIVIL = "civil", "Civil"
        CLUBS = "clubs", "Clubs"

    name = models.CharField(max_length=100)
    desc = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    # Prototype events can remain visible while their authors supply these details.
    starts_at = models.DateTimeField(null=True, blank=True, db_index=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=8, choices=Category, blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(ends_at__isnull=True)
                    | models.Q(starts_at__isnull=False, ends_at__gt=models.F("starts_at"))
                ),
                name="event_end_after_start",
            )
        ]

    def __str__(self):
        return self.name

    @property
    def map_url(self):
        query = urlencode({"api": 1, "query": self.location})
        return f"https://www.google.com/maps/search/?{query}"


class EventSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.CharField(max_length=8, choices=Event.Category)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category"], name="unique_event_subscription"
            )
        ]
