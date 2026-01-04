"""
Authentication module — signup, login, refresh, logout,
email verification, password reset, and 2FA.

Now uses the updated DB structure:
- users_col
- auth_temp_col
- rate_limit_col
"""

import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
import pyotp
from bson import ObjectId
from app.email_templates import verify_email_message, password_reset_message

from .db import (
    users_col,
    auth_temp_col,
    rate_limit_col,
)
from .config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    FRONTEND_BASE,
)
from .models import (
    UserCreate,
    UserOut,
    PasswordResetRequest,
    PasswordResetConfirm,
    TwoFASetupResponse,
    TwoFAVerifyRequest,
)
from .mailer import send_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================
# Rate Limiting
# ============================
async def enforce_rate_limit(key: str, limit: int = 20, window_sec: int = 60):
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_sec)

    # Insert current request
    await rate_limit_col.insert_one({
        "key": key,
        "created_at": now
    })

    # Count only requests in the active window
    count = await rate_limit_col.count_documents({
        "key": key,
        "created_at": {"$gte": window_start}
    })

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Slow down."
        )


# ============================
# Password Helpers
# ============================
def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ============================
# Token Helpers
# ============================
def create_access_token(data: dict, expires_delta=None):
    expire = datetime.utcnow() + (expires_delta or timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    ))
    data.update({"exp": expire})
    return jwt.encode(data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token() -> str:
    return secrets.token_urlsafe(48)


async def store_temp_token(user_id, purpose: str, token: str, hours=24):
    expire = datetime.utcnow() + timedelta(hours=hours)
    await auth_temp_col.insert_one({
        "user_id": ObjectId(user_id),
        "token": token,
        "purpose": purpose,
        "created_at": datetime.utcnow(),
        "expireAt": expire
    })


async def get_temp_token(purpose: str, token: str):
    return await auth_temp_col.find_one({
        "purpose": purpose,
        "token": token
    })


# ============================
# User Lookup
# ============================
async def get_user_by_username(username: str):
    return await users_col.find_one({"username": username})


async def get_user_by_email(email: str):
    return await users_col.find_one({"email": email})


# ============================
# Signup
# ============================
@router.post("/signup", response_model=UserOut)
async def signup(
    payload: UserCreate,
    background: BackgroundTasks,
    request: Request
):
    client_ip = request.client.host if request.client else "unknown"
    await enforce_rate_limit(f"signup:{client_ip}", limit=10)

    exists = await users_col.find_one({
        "$or": [
            {"username": payload.username},
            {"email": payload.email}
        ]
    })
    if exists:
        raise HTTPException(400, "Username or email already registered")

    doc = {
        "username": payload.username,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "is_email_verified": False,
        "two_fa_enabled": False,
        "created_at": datetime.utcnow(),
    }

    res = await users_col.insert_one(doc)
    user_id = str(res.inserted_id)

    # Email verify token
    token = secrets.token_urlsafe(48)
    await store_temp_token(user_id, "verify_email", token, hours=24)

    verify_link = f"{FRONTEND_BASE}/verify-email?token={token}&uid={user_id}"

    background.add_task(
        send_email,
        payload.email,
        "Verify your LumoAI Email",
        f"Click to verify: {verify_link}"
    )

    return UserOut(
        id=user_id,
        username=payload.username,
        email=payload.email,
        is_email_verified=False
    )


# ============================
# Login
# ============================
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    ip = request.client.host if request and request.client else "unknown"
    await enforce_rate_limit(f"login:{ip}", limit=40)

    user = await get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")

    # 2FA Check
    if user.get("two_fa_enabled"):
        raise HTTPException(403, "two_factor_required")

    access = create_access_token({"sub": user["username"]})
    refresh = create_refresh_token()

    await store_temp_token(
        user_id=str(user["_id"]),
        purpose="refresh_token",
        token=refresh,
        hours=REFRESH_TOKEN_EXPIRE_DAYS * 24
    )

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }


# ============================
# Refresh
# ============================
@router.post("/refresh")
async def refresh_token(data: dict):
    token = data.get("refresh_token")
    if not token:
        raise HTTPException(400, "Missing refresh token")

    doc = await get_temp_token("refresh_token", token)
    if not doc:
        raise HTTPException(401, "Invalid refresh token")

    user_id = doc["user_id"]
    user = await users_col.find_one({"_id": user_id})
    if not user:
        raise HTTPException(401, "Invalid user")

    # Delete old token
    await auth_temp_col.delete_one({"_id": doc["_id"]})

    # Create new pair
    new_refresh = create_refresh_token()
    await store_temp_token(user_id, "refresh_token", new_refresh)

    new_access = create_access_token({"sub": user["username"]})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh
    }


# ============================
# Logout
# ============================
@router.post("/logout")
async def logout(data: dict):
    token = data.get("refresh_token")
    if not token:
        return {"ok": True}
    await auth_temp_col.delete_many({"token": token})
    return {"ok": True}


# ============================
# Verify Email
# ============================
@router.get("/verify-email")
async def verify_email(token: str, uid: str):
    doc = await get_temp_token("verify_email", token)
    if not doc:
        raise HTTPException(400, "Invalid or expired token")

    uid_obj = ObjectId(uid)

    if doc["user_id"] != uid_obj:
        raise HTTPException(400, "Invalid or expired token")

    result = await users_col.update_one(
        {"_id": uid_obj},
        {"$set": {"is_email_verified": True}}
    )

    if result.modified_count != 1:
        raise HTTPException(500, "Email verification failed")

    await auth_temp_col.delete_one({"_id": doc["_id"]})

    return {"ok": True, "message": "Email verified"}



# ============================
# Resend verify link
# ============================
@router.post("/resend-verification")
async def resend_verification(email: str, background: BackgroundTasks):
    user = await get_user_by_email(email)
    if not user:
        return {"ok": True}

    token = secrets.token_urlsafe(48)
    await store_temp_token(str(user["_id"]), "verify_email", token)

    link = f"{FRONTEND_BASE}/verify-email?token={token}&uid={user['_id']}"

    background.add_task(send_email, email, "Verify your LumoAI Email Address", verify_email_message(user["username"], link))

    return {"ok": True}


# ============================
# Password Reset Request
# ============================
@router.post("/password-reset/request")
async def request_reset(payload: PasswordResetRequest, background: BackgroundTasks):
    user = await get_user_by_email(payload.email)
    if not user:
        return {"ok": True}

    token = secrets.token_urlsafe(48)
    await store_temp_token(str(user["_id"]), "password_reset", token, hours=2)

    link = f"{FRONTEND_BASE}/password-reset/confirm?token={token}&uid={user['_id']}"

    background.add_task(send_email, payload.email, "Reset your LumoAI password", password_reset_message(user["username"], link))

    return {"ok": True}


# ============================
# Password Reset Confirm
# ============================
@router.post("/password-reset/confirm")
async def reset_confirm(payload: PasswordResetConfirm):
    print("RESET TOKEN:", payload.token)
    doc = await get_temp_token("password_reset", payload.token)

    if not doc:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user_id = doc["user_id"]

    await users_col.update_one(
        {"_id": user_id},
        {"$set": {"hashed_password": hash_password(payload.new_password)}}
    )

    # ❗ invalidate token after use
    await auth_temp_col.delete_one({"_id": doc["_id"]})

    return {"ok": True}



# ============================
# 2FA Setup
# ============================
@router.post("/2fa/setup", response_model=TwoFASetupResponse)
async def twofa_setup(username: str):
    user = await get_user_by_username(username)
    if not user:
        raise HTTPException(404, "User not found")

    secret = pyotp.random_base32()
    otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="MentalChat"
    )

    await store_temp_token(
        str(user["_id"]),
        purpose="2fa_setup",
        token=secret,
        hours=24
    )

    return {"otp_auth_url": otp_uri, "secret": secret}


# ============================
# 2FA Verify
# ============================
@router.post("/2fa/verify")
async def twofa_verify(payload: TwoFAVerifyRequest):

    user = await get_user_by_username(payload.username)
    if not user:
        raise HTTPException(404, "User not found")

    # ------------ SETUP MODE -------------
    if payload.otp_code_secret:
        doc = await get_temp_token("2fa_setup", payload.otp_code_secret)
        if not doc or doc["user_id"] != user["_id"]:
            raise HTTPException(400, "No pending 2FA setup")

        totp = pyotp.TOTP(doc["token"])
        if not totp.verify(payload.otp_code):
            raise HTTPException(400, "Invalid OTP")

        # save secret permanently
        await users_col.update_one(
            {"_id": user["_id"]},
            {"$set": {
                "two_fa_enabled": True,
                "two_fa_secret": doc["token"]
            }}
        )
        await auth_temp_col.delete_one({"_id": doc["_id"]})
        return {"ok": True, "mode": "setup"}

    # ------------ LOGIN MODE -------------
    if user.get("two_fa_enabled"):
        secret = user.get("two_fa_secret")
        if not secret:
            raise HTTPException(400, "2FA enabled but secret missing!")

        totp = pyotp.TOTP(secret)
        if not totp.verify(payload.otp_code):
            raise HTTPException(400, "Invalid OTP")

        return {
            "ok": True,
            "mode": "login",
            "token": create_access_token({"sub": user["username"]})
        }

    raise HTTPException(400, "2FA not enabled")





# ============================
# Current User
# ============================
async def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")

    user = await users_col.find_one({"username": username})
    if not user:
        raise HTTPException(401, "Invalid token")

    return user
