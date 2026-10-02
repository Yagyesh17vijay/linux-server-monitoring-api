from fastapi import FastAPI
from fastapi import Depends
from app.core.dependencies import get_current_user

from app.database.database import engine, Base
from app.database import models
from app.routes.auth import router as auth_router


app = FastAPI(title="Linux Server Monitoring API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "Linux Server Monitoring API is running"}

@app.get("/api/v1/auth/test-protected")
def test_protected_route(
    username: str = Depends(get_current_user)
):
    return {
        "message": "Authentication successful",
        "username": username
    }

