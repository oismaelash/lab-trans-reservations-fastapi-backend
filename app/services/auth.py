from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Optional

security = HTTPBearer()


def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Extracts and validates the JWT token, returning the authenticated user's email.
    """
    token = credentials.credentials
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        email = payload.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: email não encontrado"
            )
        
        return email
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro ao validar token: {str(e)}"
        )


def get_current_user_email_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[str]:
    """
    Optional version of authentication - returns None if there's no token.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        email = payload.get("email")
        return email
    except:
        return None

