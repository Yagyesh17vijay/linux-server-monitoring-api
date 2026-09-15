from fastapi import FastAPI

from app.database.database import engine, Base
from app.database import models
from app.routes.auth import router as auth_router


app = FastAPI(title="Linux Server Monitoring API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Linux Server Monitoring API is running"}