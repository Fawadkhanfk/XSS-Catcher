from endpoints import auth
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
