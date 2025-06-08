import jwt
import logging
from fastapi import HTTPException, Header
from config.settings import JWT_SECRET_KEY, JWT_ALGORITHM

logger = logging.getLogger(__name__)

async def verify_token(authorization: str = Header(...)) -> str:
    try:
        if not authorization:
            logger.error("No authorization header provided")
            raise HTTPException(status_code=401, detail="No authorization header provided")
        logger.info(f"Authorization header: {authorization}")
        if not authorization.startswith("Bearer "):
            logger.error(f"Invalid authorization header format: {authorization}")
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
            
        token = authorization.split(" ")[1]
        logger.info(f"Verifying token: {token[:10]}...")
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            logger.debug(f"Token verified successfully for user: {payload.get('sub')}")
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e)) 