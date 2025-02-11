from fastapi import APIRouter, Depends, HTTPException, Body, Request
from bson import ObjectId
from app.core.database import posts_collection
from app.core.security import get_current_user
from app.core.utils import convert_objectid
import datetime

router = APIRouter()

# ✅ 게시글 생성 (JWT 자동 인증)
@router.post("/")
async def create_post(request: Request, title: str = Body(...), content: str = Body(...)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    post = {
        "title": title,
        "content": content,
        "author": user["email"],
        "created_at": datetime.utcnow(),
        "likes": 0,
        "dislikes": 0,
        "views": 0
    }
    result = await posts_collection.insert_one(post)
    return {"id": str(result.inserted_id), **post}

# ✅ 특정 게시글 조회
@router.get("/{post_id}")
async def get_post(post_id: str):
    post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # ✅ 조회수 증가
    await posts_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"views": 1}})
    
    return convert_objectid(post)
