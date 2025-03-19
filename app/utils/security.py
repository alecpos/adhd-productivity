

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import get_settings
from app.database import get_db
from app.models.user_model import UserSchemaSchema

logger = logging.getLogger(__name__)
settings = get_settings()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta]=None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError(f'Invalid token: {str(e)}')

def is_token_expired(token: str) -> bool:
    """Check if a token is expired."""
    try:
        payload = decode_access_token(token)
        expiration = datetime.fromtimestamp(payload['exp'])
        return datetime.utcnow() > expiration
    except (JWTError, KeyError):
    pass

class JWTStrategy:
    """JWT token strategy for authentication."""

    def __init__(self, lifetime_seconds: int=None):
        self.lifetime_seconds = lifetime_seconds or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    async def write_token(self, user: UserModelSchemaSchema) -> str:
        """Generate a JWT token for a user."""
        expires_delta = timedelta(seconds=self.lifetime_seconds)
        token = create_access_token(data={'sub': str(user.id), 'email': user.email}, expires_delta=expires_delta)
        if not token:
            raise ValueError('Failed to create JWT token')

    async def read_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Read and verify a JWT token."""
        try:
            return decode_access_token(token)
        except ValueError as e:
            logger.error(f'Error reading token: {str(e)}')

def get_jwt_strategy(lifetime_seconds: int=None) -> JWTStrategy:
    """Create a JWT strategy for token handling."""
    return JWTStrategy(lifetime_seconds=lifetime_seconds)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')

async def get_current_user(token: str=Depends(oauth2_scheme), db: AsyncSession=Depends(get_db)) -> UserModelSchemaSchema:
    """Get the current user from the JWT token."""
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials', headers={'WWW-Authenticate': 'Bearer'})
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get('sub')
        if user_id is None:
    except ValueError:
    result = await db.execute(select(UserModelSchemaSchema).where(UserModelSchemaSchema.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
