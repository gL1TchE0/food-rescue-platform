"""
Unit tests for auth.py – password hashing, JWT tokens, and user authentication.
"""
import pytest
from datetime import timedelta
from fastapi import HTTPException

from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    authenticate_user,
)
from models import User, UserRoleEnum


# ============= Password Utilities =============


class TestPasswordHashing:
    """Tests for get_password_hash and verify_password."""

    def test_get_password_hash_deterministic(self):
        """Same password should always produce the same hash."""
        h1 = get_password_hash("hello")
        h2 = get_password_hash("hello")
        assert h1 == h2

    def test_get_password_hash_is_hex(self):
        """Hash should be a 64-char hex string (SHA-256)."""
        h = get_password_hash("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_verify_password_correct(self):
        """Correct password should return True."""
        hashed = get_password_hash("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_password_incorrect(self):
        """Wrong password should return False."""
        hashed = get_password_hash("mypassword")
        assert verify_password("wrongpassword", hashed) is False


# ============= JWT Token Utilities =============


class TestJWTTokens:
    """Tests for create_access_token and decode_access_token."""

    def test_create_access_token_returns_string(self):
        """Token should be a non-empty string."""
        token = create_access_token(data={"sub": "user@example.com"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        """Decoding a valid token should return correct TokenData."""
        token = create_access_token(
            data={"sub": "user@example.com", "user_id": 1, "role": "NGO"}
        )
        token_data = decode_access_token(token)
        assert token_data.email == "user@example.com"
        assert token_data.user_id == 1
        assert token_data.role == "NGO"

    def test_decode_access_token_invalid(self):
        """Decoding a garbage token should raise HTTPException 401."""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("this.is.not.a.valid.token")
        assert exc_info.value.status_code == 401

    def test_decode_access_token_expired(self):
        """Decoding an expired token should raise HTTPException 401."""
        token = create_access_token(
            data={"sub": "user@example.com"},
            expires_delta=timedelta(seconds=-1),  # already expired
        )
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401

    def test_decode_access_token_missing_sub(self):
        """Token without 'sub' claim should raise HTTPException 401."""
        token = create_access_token(data={"user_id": 1})  # no 'sub'
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401


# ============= authenticate_user =============


class TestAuthenticateUser:
    """Tests for authenticate_user with a real DB session."""

    def test_authenticate_user_success(self, db_session, sample_user):
        """Valid credentials should return the User object."""
        user = authenticate_user(db_session, "testuser@example.com", "password123")
        assert user is not None
        assert user.email == "testuser@example.com"

    def test_authenticate_user_wrong_password(self, db_session, sample_user):
        """Wrong password should return None."""
        user = authenticate_user(db_session, "testuser@example.com", "wrongpass")
        assert user is None

    def test_authenticate_user_nonexistent_email(self, db_session):
        """Non-existent email should return None."""
        user = authenticate_user(db_session, "noone@nowhere.com", "anything")
        assert user is None
