from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Event


class EventCreationTests(TestCase):
    password = "Campus-Event-Demo-482!"

    @classmethod
    def setUpTestData(cls):
        cls.student = get_user_model().objects.create_user(
            username="event_creator", password=cls.password
        )

    def test_event_pages_redirect_to_login_and_return_after_sign_in(self):
        login_url = reverse("login")
        for route in ("event_list", "add_event"):
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

    def test_invalid_submission_shows_error_and_keeps_entered_values(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_event"),
            {"name": "Library study session", "location": "", "desc": "Open to all"},
        )

        self.assertFormError(response.context["form"], "location", "This field is required.")
        self.assertContains(response, "This field is required.")
        self.assertContains(response, 'value="Library study session"')
        self.assertContains(response, 'value="Open to all"')
        self.assertFalse(Event.objects.exists())

    def test_valid_submission_uses_the_signed_in_student_as_creator(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("add_event"),
            {"name": "Library study session", "location": "Library", "desc": "Open to all"},
        )

        self.assertRedirects(response, reverse("event_list"))
        self.assertEqual(Event.objects.get().submitted_by, self.student)
        self.assertContains(self.client.get(reverse("event_list")), self.student.username)
