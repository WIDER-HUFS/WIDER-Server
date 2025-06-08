from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter()
security = HTTPBearer()

def create_access_token(user_id: str) -> str:
    """JWT 토큰을 생성합니다."""
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {
        "user_id": user_id,
        "exp": expire
    }
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """JWT 토큰을 검증하고 user_id를 반환합니다."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

@router.get("/verify")
async def verify_auth(user_id: str = Depends(verify_token)):
    """토큰을 검증하고 사용자 ID를 반환합니다."""
    return {"user_id": user_id} 