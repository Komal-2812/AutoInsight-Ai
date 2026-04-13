from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings
import secrets

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ── PASSWORD ─────────────────────────────

def hash_password(password: str) -> str:
    # SAFE: bcrypt handles internally
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT TOKEN ────────────────────────────

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


# ── EMAIL TOKEN ──────────────────────────

def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)