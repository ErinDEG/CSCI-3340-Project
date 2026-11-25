from datetime import datetime, timedelta, timezone as utc_timezone
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Event, EventSubscription


@override_settings(TIME_ZONE="America/Chicago")
class EventTests(TestCase):
    password = "Campus-Event-Demo-482!"
    event_data = {
        "name": "Library study session",
        "location": "Library & Learning Center, Main Street",
        "desc": "Open to all",
        "category": "academic",
        "starts_at": "2026-11-30T23:30",
        "ends_at": "2026-12-01T00:30",
    }

    @classmethod
    def setUpTestData(cls):
        cls.student = get_user_model().objects.create_user(
            username="event_creator", password=cls.password
        )
        cls.other_student = get_user_model().objects.create_user(username="other_student")

    def test_event_pages_redirect_to_login_and_return_after_sign_in(self):
        login_url = reverse("login")
        for route in ("event_list", "add_event", "event_subscriptions"):
            with self.subTest(route=route):
                event_url = reverse(route)
                self.assertRedirects(
                    self.client.get(event_url), f"{login_url}?next={event_url}"
                )

        add_url = reverse("add_event")
        response = self.client.post(
            f"{login_url}?next={add_url}",
            {"username": self.student.username, "password": self.password},
        )
        self.assertRedirects(response, add_url)

    def test_invalid_submission_keeps_values_and_explains_errors(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_event"),
            {**self.event_data, "location": "", "ends_at": "2026-11-30T22:00"},
        )

        self.assertFormError(response.context["form"], "location", "This field is required.")
        self.assertFormError(
            response.context["form"], "ends_at", "The end time must be after the start time."
        )
        self.assertContains(response, 'value="Library study session"')
        self.assertContains(response, "Open to all")
        self.assertFalse(Event.objects.exists())

    def test_new_events_require_a_start_and_a_category(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_event"), {**self.event_data, "starts_at": "", "category": ""}
        )

        for field in ("starts_at", "category"):
            self.assertFormError(response.context["form"], field, "This field is required.")
        self.assertFalse(Event.objects.exists())

    def test_creation_uses_campus_time_and_redirects_to_the_event_month(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_event"), {**self.event_data, "submitted_by": self.other_student.pk}
        )

        event = Event.objects.get()
        self.assertEqual(event.submitted_by, self.student)
        self.assertEqual(
            event.starts_at, datetime(2026, 12, 1, 5, 30, tzinfo=utc_timezone.utc)
        )
        month_url = reverse("event_list", query={"month": "2026-11"})
        self.assertRedirects(response, f"{month_url}#event-{event.pk}")

        november = self.client.get(month_url)
        self.assertContains(november, self.student.username)
        self.assertContains(november, 'href="#day-2026-11-30"')
        self.assertContains(november, 'datetime="2026-11-30T23:30:00-06:00"')
        self.assertNotContains(
            self.client.get(reverse("event_list", query={"month": "2026-12"})), event.name
        )
        self.assertEqual(
            parse_qs(urlsplit(event.map_url).query),
            {"api": ["1"], "query": [self.event_data["location"]]},
        )
        self.assertContains(november, event.map_url.replace("&", "&amp;"))

    def test_calendar_filter_and_month_navigation(self):
        self.client.force_login(self.student)
        starts_at = datetime(2026, 11, 10, 12, tzinfo=utc_timezone.utc)
        Event.objects.create(
            name="Campus finals workshop", location="Library",
            starts_at=starts_at, category=Event.Category.ACADEMIC,
        )
        Event.objects.create(
            name="Intramural soccer", location="Court",
            starts_at=starts_at, category=Event.Category.SPORTS,
        )
        calendar_url = reverse("event_list")
        response = self.client.get(calendar_url, {"month": "2026-11", "category": "sports"})

        self.assertContains(response, "Intramural soccer")
        self.assertNotContains(response, "Campus finals workshop")
        self.assertContains(response, "month=2026-12&amp;category=sports")
        self.assertEqual(self.client.get(calendar_url, {"month": "2026-13"}).status_code, 404)
        self.assertEqual(self.client.get(calendar_url, {"category": "unknown"}).status_code, 404)

    def test_legacy_event_can_be_scheduled_only_by_its_author(self):
        event = Event.objects.create(
            name=self.event_data["name"], location="Library", submitted_by=self.student
        )
        edit_url = reverse("edit_event", args=[event.pk])
        self.client.force_login(self.other_student)
        self.assertEqual(self.client.post(edit_url, self.event_data).status_code, 404)
        event.refresh_from_db()
        self.assertIsNone(event.starts_at)

        self.client.force_login(self.student)
        legacy_calendar = self.client.get(reverse("event_list"))
        self.assertContains(legacy_calendar, "Events without a date (1)")
        self.assertContains(legacy_calendar, event.name)
        self.assertEqual(self.client.post(edit_url, self.event_data).status_code, 302)
        event.refresh_from_db()
        self.assertIsNotNone(event.starts_at)

    def test_subscriptions_are_personal_and_update_the_upcoming_feed(self):
        soon = timezone.now() + timedelta(days=1)
        for name, category, starts_at in (
            ("Upcoming workshop", Event.Category.ACADEMIC, soon),
            ("Upcoming match", Event.Category.SPORTS, soon),
            ("Past workshop", Event.Category.ACADEMIC, soon - timedelta(days=2)),
        ):
            Event.objects.create(name=name, category=category, starts_at=starts_at, location="Hall")

        feed_url = reverse("event_subscriptions")
        follow_url = reverse("update_event_subscription", args=["academic"])
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(follow_url).status_code, 405)
        for _ in range(2):
            self.assertRedirects(self.client.post(follow_url, {"action": "follow"}), feed_url)
        self.assertEqual(EventSubscription.objects.filter(user=self.student).count(), 1)
        response = self.client.get(feed_url)
        self.assertContains(response, "Upcoming workshop")
        self.assertNotContains(response, "Upcoming match")
        self.assertNotContains(response, "Past workshop")

        self.client.force_login(self.other_student)
        self.assertNotContains(self.client.get(feed_url), "Upcoming workshop")
        self.assertEqual(self.client.post(follow_url, {"action": "invalid"}).status_code, 400)
        self.assertEqual(EventSubscription.objects.count(), 1)

        self.client.force_login(self.student)
        self.assertRedirects(self.client.post(follow_url, {"action": "unfollow"}), feed_url)
        self.assertNotContains(self.client.get(feed_url), "Upcoming workshop")
        self.assertFalse(EventSubscription.objects.exists())

    def test_subscription_changes_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(
            reverse("update_event_subscription", args=["academic"]), {"action": "follow"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(EventSubscription.objects.exists())
