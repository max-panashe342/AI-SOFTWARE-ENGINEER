from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthenticatedUser, get_current_user
from app.database import get_db
from app.models import UserProfile
from app.schemas import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/api/me", tags=["profile"])


def get_or_create_profile(db: Session, user: AuthenticatedUser) -> UserProfile:
    profile = db.scalar(select(UserProfile).where(UserProfile.supabase_user_id == user.id))
    if profile is None:
        profile = UserProfile(supabase_user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def profile_response(profile: UserProfile, user: AuthenticatedUser) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        email=user.email,
        display_name=profile.display_name,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
) -> ProfileResponse:
    return profile_response(get_or_create_profile(db, user), user)


@router.patch("", response_model=ProfileResponse)
def update_my_profile(
    profile_update: ProfileUpdate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
) -> ProfileResponse:
    profile = get_or_create_profile(db, user)
    if profile_update.display_name is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="display_name is required.")
    profile.display_name = profile_update.display_name
    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return profile_response(profile, user)
