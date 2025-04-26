import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.routers.users_router import router as user_router
from src.routers.infra_router import router as infra_router
from src.routers.operations_router import router as operations_router


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

app.include_router(user_router)
app.include_router(infra_router)
app.include_router(operations_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0"
    )
