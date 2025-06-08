from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
import jwt
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """JWT 토큰을 생성합니다."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# @router.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     """사용자 로그인 및 토큰 발급"""
#     # TODO: 실제 사용자 인증 로직 구현
#     # 현재는 임시로 모든 로그인을 허용
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": form_data.username},
#         expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify")
async def verify_token(token: str = Depends(oauth2_scheme)):
    """토큰 검증"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {"valid": True, "username": payload.get("sub")}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 