from fastapi import FastAPI
from app.routes import auth, posts, categories, programs
from app.core.database import initialize_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield

app = FastAPI(lifespan=lifespan, redirect_slashes=False)  # 🔥 `redirect_slashes=False` 추가

app.include_router(auth.router, prefix="/auth")
app.include_router(posts.router)
app.include_router(categories.router, prefix="/categories")
app.include_router(programs.router, prefix="/programs")

@app.get("/")
async def root():
    return {"message": "Welcome to Safari Community!"}
