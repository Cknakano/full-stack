from app.core import security

def test_password_hash_roundtrip():
    pw = "S3cret!"
    h = security.get_password_hash(pw)
    assert security.verify_password(pw, h)
    assert not security.verify_password("wrong", h)
