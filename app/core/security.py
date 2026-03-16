
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# --- JWT Settings ---
SECRET_KEY = "supersecretkey"  # Or use os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
BCRYPT_MAX_BYTES = 72  # bcrypt hard limit

def hash_password(password: str) -> str:
    """
    Hash a password safely with bcrypt.
    Truncates to 72 bytes to avoid ValueError.
    """
    password_bytes = password.encode("utf-8")[:BCRYPT_MAX_BYTES]
    return pwd_context.hash(password_bytes)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password safely.
    """
    plain_bytes = plain_password.encode("utf-8")[:BCRYPT_MAX_BYTES]
    return pwd_context.verify(plain_bytes, hashed_password)

# --- JWT Token creation ---
def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)