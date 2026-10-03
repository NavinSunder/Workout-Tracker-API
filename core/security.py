from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from core.config import config

password_hash = PasswordHash.recommended()

# used to hash the password that the users enter
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# verify the password that the user enters o/p is a bool
def verify_password(password: str, hash_password: str) -> bool:
    return password_hash.verify(password, hash_password)

# to ensure that the login last for the given time (30 mins in my case)
def create_access_token(user_id: int):
    expires_in = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "exp": expires_in 
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
