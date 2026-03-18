from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from config import supabase

router = APIRouter()


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


def _extract_token(authorization: str) -> str:
    if authorization.startswith("Bearer "):
        return authorization[7:]
    return authorization


@router.post("/signup", summary="Create a new user account")
async def signup(request: AuthRequest):
    try:
        response = supabase.auth.sign_up(
            {"email": request.email, "password": request.password}
        )
        return {
            "message": "Account created. Please check your email to confirm.",
            "user": response.user.email if response.user else None,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", summary="Sign in with email and password")
async def login(request: AuthRequest):
    try:
        response = supabase.auth.sign_in_with_password(
            {"email": request.email, "password": request.password}
        )
        return {
            "access_token": response.session.access_token,
            "token_type": "bearer",
            "user": response.user.email,
        }
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid email or password") from exc


@router.post("/logout", summary="Sign out the current user")
async def logout(authorization: str = Header(...)):
    try:
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/user", summary="Get current authenticated user")
async def get_user(authorization: str = Header(...)):
    try:
        token = _extract_token(authorization)
        user_response = supabase.auth.get_user(token)
        return {
            "id": str(user_response.user.id),
            "email": user_response.user.email,
        }
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
