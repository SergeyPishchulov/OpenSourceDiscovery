from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext

from app.conf.config import CFG
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(password: str) -> bool:
    return verify_password(password, CFG.auth_hash)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, CFG.jwt.SECRET_KEY, algorithm=CFG.jwt.ALGORITHM)
    return encoded_jwt


def auth_by_jwt(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect JWT",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CFG.jwt.SECRET_KEY, algorithms=[CFG.jwt.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
