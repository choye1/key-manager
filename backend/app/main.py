from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.auth import router as auth_router
from app.api.routes.keys import router as keys_router
from app.api.routes.objects import router as objects_router
from app.api.routes.operations import router as operations_router
from app.api.routes.users import router as users_router
from app.core.db import init_db

app = FastAPI(title="Key Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://choye23324.temp.swtest.ru",
        "http://choye23324.temp.swtest.ru",
        "https://www.choye23324.temp.swtest.ru/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root():
    return {"message": "OK"}


app.include_router(auth_router)
app.include_router(objects_router)
app.include_router(keys_router)
app.include_router(operations_router)
app.include_router(users_router)
