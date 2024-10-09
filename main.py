import logging
from datetime import timedelta
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.api_v1.api import router as api_v1_router
from settings import ACCESS_TOKEN_EXPIRE_MINUTES
from api.security import Token, authenticate_user, create_access_token

log = logging.getLogger("uvicorn")

origins = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    log.info("Starting up...")
    yield
    log.info("Shutting down...")


app = FastAPI()
app.include_router(api_v1_router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
