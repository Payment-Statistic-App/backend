import os
import uvicorn

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.users.models import User
from src.users.routers.student_routers import router as student_router
from src.users.routers.admin_routers import router as admin_router
from src.users.schemas import Token
from src.users.services import UserService


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.system("alembic upgrade head")
    yield


app = FastAPI(
    title="Payment-service",
    lifespan=lifespan
)


@app.get("/ping")
async def ping_pong():
    return "pong"


@app.post("/login", response_model=Token)
async def authenticate_user_jwt(user: User = Depends(UserService().authenticate_user)) -> Token:
    access_token = UserService().create_access_token(user)
    refresh_token = UserService().create_refresh_token(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0"
    )
