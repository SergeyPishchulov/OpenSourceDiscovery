from datetime import datetime, timezone, timedelta

from passlib.context import CryptContext

from conf.config import CFG
import jwt
from jwt.exceptions import InvalidTokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password)->bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(password: str)->bool:
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
