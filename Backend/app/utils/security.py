from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
import secrets
import hashlib  # ✅ NEW

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── 🔐 PASSWORD FUNCTIONS (FIXED) ────────────────────────────────────────────
def hash_password(password: str) -> str:
    # ✅ Step 1: Convert to SHA256 (removes 72 byte limit)
    password = hashlib.sha256(password.encode()).hexdigest()
    # ✅ Step 2: Hash with bcrypt
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # ✅ Apply same SHA256 before verifying
    plain = hashlib.sha256(plain.encode()).hexdigest()
    return pwd_context.verify(plain, hashed)


# ── 🔐 TOKEN FUNCTIONS ───────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


# ── 🔐 EMAIL TOKEN ───────────────────────────────────────────────────────────
def generate_verification_token() -> str:
    return secrets.token_urlsafe(32)