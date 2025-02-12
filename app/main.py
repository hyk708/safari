from fastapi import FastAPI
from app.routes import auth, post, categories, programs, presets
from app.core.database import initialize_database
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield

app = FastAPI(lifespan=lifespan, redirect_slashes=False)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(post.router, prefix="/post", tags=["post"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(programs.router, prefix="/programs", tags=["programs"])
app.include_router(presets.router, prefix="/presets", tags=["presets"])

@app.get("/")
async def root():
    return {"message": "Welcome to Safari Community!"}
