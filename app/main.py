from fastapi import FastAPI
from app.api.routes import auth, users, patients

app = FastAPI()

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, tags=["Users"])
app.include_router(patients.router, tags=["Patients"])
