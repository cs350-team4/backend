from datetime import datetime, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from api.db.engine import client_engine, local_engine
from api.dependencies import GetSession
from api.models import Client, GenerateToken, OwnedModel
from api.routers.game import router as game_router
from api.routers.prize import router as prize_router
from api.settings import settings


def create_db_and_tables() -> None:
    OwnedModel.metadata.create_all(local_engine)


origins = ["http://localhost:6006", "http://localhost:3000"]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


assert isinstance(game_router, APIRouter)
app.include_router(game_router, prefix="/games")
app.include_router(prize_router, prefix="/prizes")


@app.post("/auth/generateToken")
def generate_token(
    *, session: Session = Depends(GetSession(client_engine)), payload: GenerateToken
):
    stmt = select(Client).where(Client.username == payload.username)
    result = session.exec(stmt).first()
    if result is None:
        raise HTTPException(status_code=403, detail="Authentication failed")
    if bcrypt.checkpw(payload.password.encode("utf8"), result.password.encode("utf8")):
        jwToken = jwt.encode(
            {"name": result.username, "iat": datetime.now(tz=timezone.utc)},
            settings.PRIVATE_KEY,
            algorithm="ES256",
        )
        return {"auth_token": jwToken}
    else:
        raise HTTPException(status_code=403, detail="Authentication failed")


@app.get("/auth/publicKey")
def public_key():
    return {"publicKey": settings.PUBLIC_KEY}
