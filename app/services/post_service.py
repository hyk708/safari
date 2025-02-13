import os
from fastapi import UploadFile
from app.core.database import posts_collection
from bson import ObjectId, errors
from datetime import datetime
from typing import Optional, List
import json

UPLOAD_FOLDER = "static/uploads"

async def save_image(file: UploadFile) -> str:
    """이미지를 저장하고 경로를 반환"""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())
    return f"/{file_location}"

async def create_post(title: str, content: str, preset_id: Optional[str], is_public: bool, created_by: str, file: Optional[UploadFile] = None):
    """게시글 생성"""
    image_url = await save_image(file) if file else None
    post = {
        "title": title,
        "content": content,
        "preset_id": preset_id,
        "created_by": created_by,
        "is_public": is_public,
        "image_url": image_url,
        "like_count": 0,
        "dislike_count": 0,
        "comment_count": 0,
        "scrap_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = await posts_collection.insert_one(post)
    return {
        "id": str(result.inserted_id),
        **post
    }

async def get_posts():
    """모든 공개된 게시글 조회"""
    posts = await posts_collection.find({"is_public": True}).sort("created_at", -1).to_list(100)
    return [
        {
            "id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "preset_id": post.get("preset_id", None),
            "image_url": post.get("image_url"),
            "is_public": post["is_public"],
            "like_count": post["like_count"],
            "dislike_count": post["dislike_count"],
            "comment_count": post["comment_count"],
            "scrap_count": post["scrap_count"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
        }
        for post in posts
    ]

async def get_post(post_id: str):
    """특정 게시글 조회"""
    try:
        obj_id = ObjectId(post_id)
    except errors.InvalidId:
        return None
    post = await posts_collection.find_one({"_id": obj_id})
    if not post:
        return None
    return {
        "id": str(post["_id"]),
        "title": post["title"],
        "content": post["content"],
        "preset_id": post.get("preset_id"),
        "image_url": post.get("image_url"),
        "is_public": post["is_public"],
        "like_count": post["like_count"],
        "dislike_count": post["dislike_count"],
        "comment_count": post["comment_count"],
        "scrap_count": post["scrap_count"],
        "created_at": post["created_at"],
        "updated_at": post["updated_at"],
    }

async def update_post(post_id: str, title: Optional[str], content: Optional[str], preset_id: Optional[str], is_public: Optional[bool], image_url: Optional[str] = None):
    """게시글 수정"""
    obj_id = ObjectId(post_id)
    update_fields = {}

    if title is not None:
        update_fields["title"] = title
    if content is not None:
        update_fields["content"] = content
    if preset_id is not None:
        update_fields["preset_id"] = preset_id
    if is_public is not None:
        update_fields["is_public"] = is_public
    if image_url is not None:
        update_fields["image_url"] = image_url

    update_fields["updated_at"] = datetime.utcnow()

    if update_fields:
        await posts_collection.update_one({"_id": obj_id}, {"$set": update_fields})

    updated_post = await posts_collection.find_one({"_id": obj_id})

    if updated_post:
        updated_post["id"] = str(updated_post["_id"])
        del updated_post["_id"]

    return updated_post

async def delete_post(post_id: str):
    """게시글 삭제"""
    obj_id = ObjectId(post_id)
    await posts_collection.delete_one({"_id": obj_id})

async def update_post_reactions(post_id: str, like: bool):
    """게시글 좋아요/싫어요 업데이트"""
    try:
        obj_id = ObjectId(post_id)
    except errors.InvalidId:
        return None
    update_field = "like_count" if like else "dislike_count"
    await posts_collection.update_one(
        {"_id": obj_id},
        {"$inc": {update_field: 1}}
    )

async def update_comment_count(post_id: str, change: int):
    """댓글 수 업데이트 (+1 or -1)"""
    try:
        obj_id = ObjectId(post_id)
    except errors.InvalidId:
        return None
    await posts_collection.update_one(
        {"_id": obj_id},
        {"$inc": {"comment_count": change}}
    )

async def update_scrap_count(post_id: str, increment: int):
    """스크랩 수 업데이트"""
    obj_id = ObjectId(post_id)
    await posts_collection.update_one({"_id": obj_id}, {"$inc": {"scrap_count": increment}})

async def create_post_from_preset(preset_json: str, user_email: str):
    """프리셋 JSON을 기반으로 게시글 생성"""
    preset_data = json.loads(preset_json)

    post = {
        "title": f"Shared Preset: {preset_data['name']}",
        "content": f"Preset Description: {preset_data['description']}\nPrograms: {', '.join(preset_data['programs'])}",
        "author": user_email,
        "created_at": datetime.utcnow(),
        "preset_data": preset_data
    }

    result = await posts_collection.insert_one(post)
    post["_id"] = str(result.inserted_id)
    return post