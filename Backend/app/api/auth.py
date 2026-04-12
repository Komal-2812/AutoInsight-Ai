from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserProfile
from app.utils.security import hash_password, verify_password, create_access_token, decode_token, generate_verification_token
from app.services.email_service import send_verification_email
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/signup", status_code=201)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    token = generate_verification_token()
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        verification_token=token,
        is_verified=True  # ← this line must be here
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    try:
        send_verification_email(data.email, token)
    except Exception as e:
        print(f"[Email] Failed silently: {e}")
    return {"message": "Account created. Please verify your email."}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")
    token = create_access_token({"sub": user.id, "email": user.email})
    return {"access_token": token}

@router.get("/profile", response_model=UserProfile)
def profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    user.is_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully. You can now log in."}