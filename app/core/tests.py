from django.test import TestCase
from django.urls import reverse


class AccountPrototypeTests(TestCase):
    def test_guest_can_register_save_a_profile_and_return_after_logging_out(self):
        home = reverse("home")
        profile = reverse("profile")
        login = reverse("login")
        password = "Campus-Account-Demo-498!"

        self.assertContains(self.client.get(home), "Create an account")
        self.assertRedirects(self.client.get(profile), f"{login}?next={profile}")

        registration = self.client.post(
            reverse("register"),
            {
                "username": "new_student",
                "password1": password,
                "password2": password,
            },
        )
        self.assertRedirects(registration, home)
        self.assertContains(self.client.get(home), "Welcome, new_student.")

        saved_profile = self.client.post(
            profile, {"first_name": "Taylor", "last_name": "Lee"}, follow=True
        )
        self.assertRedirects(saved_profile, profile)
        self.assertContains(saved_profile, "Your profile was saved.")
        self.assertContains(self.client.get(home), "Welcome, Taylor.")

        self.assertRedirects(self.client.post(reverse("logout")), home)
        self.assertRedirects(self.client.get(profile), f"{login}?next={profile}")

        sign_in = self.client.post(
            login,
            {"username": "new_student", "password": password, "next": profile},
            follow=True,
        )
        self.assertRedirects(sign_in, profile)
        self.assertContains(sign_in, 'value="Taylor"')
        self.assertContains(sign_in, 'value="Lee"')
