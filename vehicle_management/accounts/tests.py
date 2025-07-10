from django.contrib.auth.models import User
from django.test import TestCase

from .decorators import get_profile
from .forms import CustomUserCreationForm
from .models import ROLE_MANAGER, UserProfile


class SignupFormTests(TestCase):
    def test_signup_creates_profile_with_role(self):
        form = CustomUserCreationForm(
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password1": "s3cret-pass-99",
                "password2": "s3cret-pass-99",
                "role": ROLE_MANAGER,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, ROLE_MANAGER)
        self.assertTrue(profile.is_manager)


class GetProfileTests(TestCase):
    def test_get_profile_creates_guard_default_when_missing(self):
        user = User.objects.create_user("bob", password="x")
        profile = get_profile(user)
        self.assertFalse(profile.is_manager)
        # Idempotent: no duplicate profile on second call.
        self.assertEqual(get_profile(user).pk, profile.pk)
