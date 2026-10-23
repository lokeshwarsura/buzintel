import pytest

from backend.core.security import hash_password, verify_password


def test_scrypt_password_hash_round_trip() -> None:
    hashed = hash_password("a-long-demo-password")
    assert verify_password("a-long-demo-password", hashed)
    assert not verify_password("wrong-password-value", hashed)


def test_short_password_rejected() -> None:
    with pytest.raises(ValueError, match="12"):
        hash_password("too-short")
