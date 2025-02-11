from fastapi import FastAPI
from app.routes import auth, protected, posts, categories, programs
from app.core.database import initialize_database

app = FastAPI()

# ✅ DB 초기화 실행
@app.on_event("startup")
async def startup_db():
    await initialize_database()

app.include_router(auth.router, prefix="/auth")
app.include_router(protected.router)
app.include_router(posts.router)
app.include_router(categories.router, prefix="/categories")
app.include_router(programs.router, prefix="/programs")

@app.get("/")
async def root():
    return {"message": "Welcome to Safari Community!"}
