from dataclasses import dataclass
from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).parent.parent


@dataclass
class DataBase:
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@dataclass
class AuthJWT:
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 1440
    refresh_token_expire_days: int = 30


@dataclass
class Config:
    database: DataBase
    authJWT: AuthJWT


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        database=DataBase(
            DB_HOST=env("DB_HOST"),
            DB_PORT=env("DB_PORT"),
            DB_USER=env("DB_USER"),
            DB_PASS=env("DB_PASS"),
            DB_NAME=env("DB_NAME")
        ),
        authJWT=AuthJWT(
            private_key_path=AuthJWT.private_key_path,
            public_key_path=AuthJWT.public_key_path,
            algorithm=AuthJWT.algorithm
        ),
    )
