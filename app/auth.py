import hmac
import hashlib
from app import config

def generate_signed_token(username: str) -> str:
    return hmac.new(
        config.GIF_SECRET.encode(),
        username.encode(),
        hashlib.sha256
    ).hexdigest()

def verify_signed_token(username: str, token: str) -> bool:
    expected = generate_signed_token(username)
    return hmac.compare_digest(expected, token)