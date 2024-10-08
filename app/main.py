from fastapi import FastAPI
import uvicorn

from app.api.api_v1.api import router as api_v1_router


app = FastAPI()

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__=="__main__":
    uvicorn.run("app.main:app", port=8000, reload=True)