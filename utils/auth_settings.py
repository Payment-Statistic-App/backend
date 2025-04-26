import datetime
import bcrypt
import jwt

from config_data import constants
from config_data.config import Config, load_config
from src.models import User

settings: Config = load_config(".env")
auth_config = settings.authJWT


def create_jwt(
        token_type: str,
        token_data: dict,
        expire_minutes: int = auth_config.access_token_expire_minutes,
        expire_timedelta: datetime.timedelta | None = None
) -> str:
    jwt_payload = {constants.TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    token = encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )
    return token


def encode_jwt(
        payload: dict,
        private_key: str = auth_config.private_key_path.read_text(),
        algorithm: str = auth_config.algorithm,
        expire_minutes: int = auth_config.access_token_expire_minutes,
        expire_timedelta: datetime.timedelta | None = None
) -> str:
    now = datetime.datetime.utcnow()
    if expire_timedelta is not None:
        expire = now + expire_timedelta
    else:
        expire = now + datetime.timedelta(minutes=expire_minutes)

    to_encode = payload.copy()
    to_encode.update(exp=expire, iat=now)
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = auth_config.public_key_path.read_text(),
        algorithm: str = auth_config.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
        password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
        password: str,
        hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def create_access_token(user: User) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "login": user.login,
    }
    return create_jwt(
        token_type=constants.ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=auth_config.access_token_expire_minutes
    )


def create_refresh_token(user: User) -> str:
    jwt_payload = {
        "sub": str(user.id),
        "login": user.login,
    }
    return create_jwt(
        token_type=constants.REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=datetime.timedelta(days=auth_config.refresh_token_expire_days)
    )
