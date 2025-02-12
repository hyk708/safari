from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# 🔹 auth는 /auth 로!
from app.routes import auth  # 로그인 관련 API는 /auth로 묶는다
from app.core.database import initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield

app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # ✅ 특정 Origin만 허용
    allow_credentials=True,  # ✅ 쿠키를 포함한 요청 허용
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # ✅ 허용할 HTTP 메서드
    allow_headers=["Authorization", "Content-Type"],  # ✅ 허용할 HTTP 헤더
)

# 🔹 Jinja2 템플릿
templates = Jinja2Templates(directory="templates")

# 🔹 정적 파일
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ auth 라우터 등록 (prefix=/auth)
app.include_router(auth.router, prefix="/auth")

# ✅ 루트 페이지: index.html
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ 로그인 페이지: login.html
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ✅ 로그아웃
@app.get("/logout/")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response

# 카테고리 관리
@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})  # ✅ settings.html 반환
