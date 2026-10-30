import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app.auth import AuthenticatedUser, get_current_user
from app.database import Base
from app.models import UserProfile
from app.routers.profile import get_my_profile, get_or_create_profile, update_my_profile
from app.schemas import ProfileUpdate


class ProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.user = AuthenticatedUser(id="11111111-1111-1111-1111-111111111111", email="user@example.com")

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_profile_is_created_once_and_returned(self) -> None:
        first = get_my_profile(self.session, self.user)
        second = get_my_profile(self.session, self.user)

        self.assertEqual(first.id, second.id)
        self.assertIsNone(first.display_name)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(UserProfile)), 1)

    def test_profile_update_only_changes_authenticated_profile(self) -> None:
        get_or_create_profile(self.session, self.user)
        updated = update_my_profile(ProfileUpdate(display_name="  Ada Lovelace  "), self.session, self.user)

        self.assertEqual(updated.display_name, "Ada Lovelace")
        self.assertEqual(self.session.scalar(select(func.count()).select_from(UserProfile)), 1)

    def test_empty_display_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            ProfileUpdate(display_name="   ")

    def test_missing_authentication_is_rejected(self) -> None:
        with self.assertRaises(HTTPException) as context:
            get_current_user(None)

        self.assertEqual(context.exception.status_code, 401)

    def test_supabase_token_resolves_to_authenticated_user(self) -> None:
        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b'{"id":"33333333-3333-3333-3333-333333333333","email":"verified@example.com"}'

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        with patch("app.auth.SUPABASE_URL", "https://project.example"), patch(
            "app.auth.SUPABASE_PUBLISHABLE_KEY", "publishable-key"
        ), patch("app.auth.urllib.request.urlopen", return_value=FakeResponse()):
            user = get_current_user(credentials)

        self.assertEqual(user.id, "33333333-3333-3333-3333-333333333333")
        self.assertEqual(user.email, "verified@example.com")

    def test_invalid_supabase_token_is_rejected(self) -> None:
        error = HTTPError("https://example.test/auth/v1/user", 401, "invalid", {}, None)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
        with patch("app.auth.SUPABASE_URL", "https://project.example"), patch(
            "app.auth.SUPABASE_PUBLISHABLE_KEY", "publishable-key"
        ), patch("app.auth.urllib.request.urlopen", side_effect=error):
            with self.assertRaises(HTTPException) as context:
                get_current_user(credentials)

        self.assertEqual(context.exception.status_code, 401)

    def test_frontend_user_id_is_not_used_for_profile_lookup(self) -> None:
        other_user = AuthenticatedUser(id="22222222-2222-2222-2222-222222222222", email="other@example.com")
        get_or_create_profile(self.session, self.user)
        profile = get_or_create_profile(self.session, other_user)

        self.assertNotEqual(profile.supabase_user_id, self.user.id)
        self.assertEqual(self.session.scalar(select(func.count()).select_from(UserProfile)), 2)


if __name__ == "__main__":
    unittest.main()
