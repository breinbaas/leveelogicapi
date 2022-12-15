from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import sys

if not "/home/breinbaas/leveelogic" in sys.path:
    sys.path.append("/home/breinbaas/leveelogic")

from server.routes.cpt import router as CptRouter

app = FastAPI()
app.include_router(CptRouter, tags=["Cpt"], prefix="/cpt")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello from Fastapi"}
