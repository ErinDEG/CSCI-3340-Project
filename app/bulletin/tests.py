from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Announcement


class BulletinBoardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = get_user_model().objects.create_user(username="student")
        cls.other_student = get_user_model().objects.create_user(username="another_student")

    def test_guests_can_browse_but_are_sent_to_login_to_post(self):
        Announcement.objects.create(
            title="Library hours", body="Open until eight.", author=self.student
        )
        board = self.client.get(reverse("bulletin:board"))
        self.assertContains(board, "Library hours")
        self.assertContains(board, "Log in to post")
        post_url = reverse("bulletin:post")
        self.assertRedirects(
            self.client.get(post_url), f"{reverse('login')}?next={post_url}"
        )
        self.assertEqual(self.client.post(post_url, {"title": "Guest post"}).status_code, 302)
        self.assertEqual(Announcement.objects.count(), 1)

    def test_signed_in_student_can_post_and_content_is_escaped(self):
        self.client.force_login(self.student)
        board_url = reverse("bulletin:board")
        response = self.client.post(
            reverse("bulletin:post"),
            {
                "title": "Lab opening",
                "body": "<script>alert(1)</script>",
                "author": self.other_student.pk,
            },
        )
        self.assertRedirects(response, board_url)
        self.assertEqual(Announcement.objects.get().author, self.student)
        board = self.client.get(board_url)
        self.assertContains(board, "Lab opening")
        self.assertContains(board, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(board, "<script>alert(1)</script>")

    def test_only_the_author_can_edit_an_announcement(self):
        announcement = Announcement.objects.create(
            title="Original title", body="Original message", author=self.student
        )
        edit_url = reverse("bulletin:edit", args=[announcement.pk])
        post_data = {"title": "Updated title", "body": "Updated message"}
        self.client.force_login(self.other_student)
        self.assertEqual(self.client.post(edit_url, post_data).status_code, 404)
        announcement.refresh_from_db()
        self.assertEqual(announcement.title, "Original title")

        self.client.force_login(self.student)
        self.assertRedirects(self.client.post(edit_url, post_data), reverse("bulletin:board"))
        announcement.refresh_from_db()
        self.assertEqual(announcement.title, "Updated title")

    def test_invalid_posts_keep_entered_values(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("bulletin:post"), {"title": "Study room", "body": " " * 10}
        )
        self.assertFormError(response.context["form"], "body", "This field is required.")
        self.assertContains(response, 'value="Study room"')
        self.assertFalse(Announcement.objects.exists())

    def test_board_paginates_newest_first(self):
        for index in range(11):
            Announcement.objects.create(title=f"Notice {index:02}", body="Details", author=self.student)
        board_url = reverse("bulletin:board")
        first_page = self.client.get(board_url)
        self.assertContains(first_page, "Notice 10")
        self.assertNotContains(first_page, "Notice 00")
        self.assertContains(first_page, 'href="?page=2"')
        second_page = self.client.get(board_url, {"page": 2})
        self.assertContains(second_page, "Notice 00")
        self.assertNotContains(second_page, "Notice 10")

    def test_posting_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.student)
        response = client.post(reverse("bulletin:post"), {"title": "New post", "body": "Details"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Announcement.objects.exists())
