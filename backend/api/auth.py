"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import httpx
from typing import Optional
import secrets

from db.base import get_db
from db.models import User, UserRole
from schemas.user import UserCreate, UserResponse, Token, UserLogin
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from core.config import settings
from services.email_service import email_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token.
    """
    payload = decode_token(token)
    verify_token_type(payload, "access")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user


async def get_current_user_ws(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from WebSocket query string token.

    Usage: ws://localhost:8000/api/v1/ws/123?token=eyJ0eXAiOiJKV1QiLCJhbGci...
    """
    try:
        payload = decode_token(token)
        verify_token_type(payload, "access")

        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code=1008, reason="Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            await websocket.close(code=1008, reason="User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            await websocket.close(code=1008, reason="Inactive user")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return user
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        raise


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check ORCID uniqueness if provided
    if user_data.orcid:
        existing_orcid = db.query(User).filter(User.orcid == user_data.orcid).first()
        if existing_orcid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ORCID already registered"
            )

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        affiliation=user_data.affiliation,
        department=user_data.department,
        country=user_data.country,
        orcid=user_data.orcid,
        phone=user_data.phone,
        bio=user_data.bio,
        website=user_data.website,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send welcome email
    await email_service.send_welcome_email(
        user_email=new_user.email,
        user_name=new_user.full_name,
        role=new_user.role.value
    )

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login user and return access token.
    """
    # Find user
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    payload = decode_token(refresh_token)
    verify_token_type(payload, "refresh")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should delete tokens).
    """
    return {"message": "Successfully logged out"}


# ============================================================================
# ORCID OAuth Integration
# ============================================================================

# In-memory state storage (in production, use Redis)
oauth_states = {}


@router.get("/orcid/login")
async def orcid_login(redirect_uri: Optional[str] = None):
    """
    Initiate ORCID OAuth login flow.

    Returns authorization URL to redirect user to ORCID.

    Configuration required in settings:
    - ORCID_CLIENT_ID
    - ORCID_CLIENT_SECRET
    - ORCID_REDIRECT_URI (or use redirect_uri parameter)
    - ORCID_API_BASE (production or sandbox)
    """
    if not hasattr(settings, 'ORCID_CLIENT_ID') or not settings.ORCID_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ORCID OAuth is not configured. Please set ORCID_CLIENT_ID in settings."
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        'created_at': datetime.now(),
        'redirect_uri': redirect_uri or settings.FRONTEND_URL
    }

    # Build ORCID authorization URL
    orcid_base = getattr(settings, 'ORCID_API_BASE', 'https://orcid.org')
    redirect_uri_param = getattr(settings, 'ORCID_REDIRECT_URI', f"{settings.API_URL}/api/v1/auth/orcid/callback")

    auth_url = (
        f"{orcid_base}/oauth/authorize"
        f"?client_id={settings.ORCID_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=/authenticate"
        f"&redirect_uri={redirect_uri_param}"
        f"&state={state}"
    )

    return {
        "authorization_url": auth_url,
        "state": state
    }


@router.get("/orcid/callback")
async def orcid_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    Handle ORCID OAuth callback.

    - Validates state
    - Exchanges code for access token
    - Fetches ORCID profile
    - Creates new user or links to existing account
    - Returns JWT tokens
    """
    if not hasattr(settings, 'ORCID_CLIENT_ID') or not settings.ORCID_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ORCID OAuth is not configured"
        )

    # Verify state (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth state"
        )

    state_data = oauth_states.pop(state)

    # Check state age (expire after 10 minutes)
    if (datetime.now() - state_data['created_at']).seconds > 600:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth state expired"
        )

    # Exchange authorization code for access token
    orcid_base = getattr(settings, 'ORCID_API_BASE', 'https://orcid.org')
    redirect_uri = getattr(settings, 'ORCID_REDIRECT_URI', f"{settings.API_URL}/api/v1/auth/orcid/callback")

    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                f"{orcid_base}/oauth/token",
                headers={
                    "Accept": "application/json",
                },
                data={
                    "client_id": settings.ORCID_CLIENT_ID,
                    "client_secret": settings.ORCID_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri
                }
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange ORCID code: {token_response.text}"
                )

            token_data = token_response.json()
            orcid_id = token_data.get('orcid')
            orcid_access_token = token_data.get('access_token')
            name = token_data.get('name')

            if not orcid_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get ORCID iD from response"
                )

            # Fetch full ORCID profile (optional, for more details)
            # This requires /read-limited scope
            # For now, we'll use the basic info from token response

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error communicating with ORCID: {str(e)}"
            )

    # Check if user exists with this ORCID
    user = db.query(User).filter(User.orcid == orcid_id).first()

    if user:
        # Existing user - log them in
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Update last login
        user.last_login = datetime.now()
        db.commit()

    else:
        # New user - create account
        # Generate unique email placeholder (user can update later)
        temp_email = f"{orcid_id.replace('-', '')}@orcid.placeholder"

        # Check if placeholder email exists (shouldn't happen, but be safe)
        existing_temp = db.query(User).filter(User.email == temp_email).first()
        if existing_temp:
            temp_email = f"{orcid_id.replace('-', '')}.{secrets.token_hex(4)}@orcid.placeholder"

        # Parse name
        if name:
            parts = name.split()
            first_name = parts[0] if parts else ""
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        else:
            first_name = "ORCID"
            last_name = "User"

        # Create new user
        user = User(
            email=temp_email,
            first_name=first_name,
            last_name=last_name,
            orcid=orcid_id,
            role=UserRole.AUTHOR,  # Default role
            is_active=True,
            is_verified=True,  # ORCID-authenticated users are verified
            hashed_password=get_password_hash(secrets.token_urlsafe(32))  # Random password (won't be used)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Send welcome email (if they have a real email)
        if not user.email.endswith('@orcid.placeholder'):
            try:
                await email_service.send_email(
                    recipients=[user.email],
                    subject="Welcome to the Journal",
                    template_name="welcome",
                    context={
                        'user_name': f"{user.first_name} {user.last_name}",
                        'role': user.role.value
                    }
                )
            except Exception as e:
                print(f"Failed to send welcome email: {e}")

    # Create JWT tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    # Redirect to frontend with tokens
    frontend_redirect = state_data.get('redirect_uri', settings.FRONTEND_URL)
    redirect_url = f"{frontend_redirect}/auth/orcid-callback?access_token={access_token}&refresh_token={refresh_token}"

    return RedirectResponse(url=redirect_url)


@router.post("/orcid/link")
async def link_orcid(
    orcid_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Link ORCID to existing account.

    User must be logged in. Exchanges ORCID code for ORCID iD and links to account.
    """
    if not hasattr(settings, 'ORCID_CLIENT_ID') or not settings.ORCID_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ORCID OAuth is not configured"
        )

    if current_user.orcid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Account already linked to ORCID: {current_user.orcid}"
        )

    # Exchange code for ORCID iD (same process as callback)
    orcid_base = getattr(settings, 'ORCID_API_BASE', 'https://orcid.org')
    redirect_uri = getattr(settings, 'ORCID_REDIRECT_URI', f"{settings.API_URL}/api/v1/auth/orcid/callback")

    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(
                f"{orcid_base}/oauth/token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.ORCID_CLIENT_ID,
                    "client_secret": settings.ORCID_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "code": orcid_code,
                    "redirect_uri": redirect_uri
                }
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to verify ORCID code"
                )

            token_data = token_response.json()
            orcid_id = token_data.get('orcid')

            if not orcid_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get ORCID iD"
                )

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error communicating with ORCID: {str(e)}"
            )

    # Check if ORCID already linked to another account
    existing_user = db.query(User).filter(User.orcid == orcid_id).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This ORCID is already linked to another account"
        )

    # Link ORCID to current user
    current_user.orcid = orcid_id
    db.commit()
    db.refresh(current_user)

    return {
        "message": "ORCID successfully linked",
        "orcid": orcid_id
    }


@router.post("/orcid/unlink")
async def unlink_orcid(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlink ORCID from current account.
    """
    if not current_user.orcid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No ORCID linked to this account"
        )

    current_user.orcid = None
    db.commit()

    return {"message": "ORCID unlinked successfully"}
