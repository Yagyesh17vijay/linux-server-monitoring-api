from app.database.database import engine, Base
from app.database import models
from fastapi import FastAPI

app = FastAPI(title= "Linux Server Monitoring API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Linux Server Monitoring API"}
