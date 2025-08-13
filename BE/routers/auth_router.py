from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class UserInfo(BaseModel):
    uid: str
    email: str
    name: str

@router.get("/me", response_model=UserInfo)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserInfo(
        uid=current_user.get("uid", ""),
        email=current_user.get("email", ""),
        name=current_user.get("name", "")
    )

@router.post("/verify")
def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify if the provided token is valid"""
    return {"valid": True, "user": current_user}
