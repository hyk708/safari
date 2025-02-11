from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from bson import ObjectId
from datetime import datetime

# ✅ MongoDB 연결
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["safari_db"]

# ✅ 컬렉션 정의
users_collection = db["users"]
posts_collection = db["posts"]
comments_collection = db["comments"]
categories_collection = db["categories"]
programs_collection = db["programs"]
presets_collection = db["presets"]

async def initialize_database():
    """DB 초기화 및 컬렉션 생성 (필요한 경우 인덱스 추가)"""
    existing_collections = await db.list_collection_names()

    # ✅ 기본 "미분류" 카테고리 추가
    uncategorized = await categories_collection.find_one({"name": "미분류"})
    if not uncategorized:
        inserted = await categories_collection.insert_one({"name": "미분류", "created_by": "system"})
        uncategorized_id = inserted.inserted_id  # ✅ 새로 생성 시 ObjectId 저장
        print(f"✅ 기본 '미분류' 카테고리 추가됨 (ID: {uncategorized_id})")
    else:
        uncategorized_id = uncategorized["_id"]  # ✅ 기존 ObjectId 유지

    # ✅ 기본 유저 추가
    existing_user = await users_collection.find_one({"email": "testuser@example.com"})
    if not existing_user:
        user_id = await users_collection.insert_one({
            "email": "testuser@example.com",
            "name": "테스트 유저",
            "created_at": datetime.utcnow(),
            "oauth_provider": "google"
        })
        user_id = user_id.inserted_id  # ✅ ObjectId 저장
        print(f"✅ 테스트 유저 추가 완료 (ID: {user_id})")
    else:
        user_id = existing_user["_id"]

    # ✅ 기본 프로그램 추가
    existing_program = await programs_collection.find_one({"name": "테스트 프로그램"})
    if not existing_program:
        program_id = await programs_collection.insert_one({
            "name": "테스트 프로그램",
            "category_id": uncategorized_id,
            "created_by": "testuser@example.com"
        })
        print(f"✅ 테스트 프로그램 추가 완료 (ID: {program_id.inserted_id})")

    # ✅ 기본 게시글 추가
    existing_post = await posts_collection.find_one({"title": "테스트 게시글"})
    if not existing_post:
        inserted_post = await posts_collection.insert_one({
            "title": "테스트 게시글",
            "content": "MongoDB 초기화 테스트 중",
            "author_id": user_id,
            "category_id": uncategorized_id,
            "image_url": None,
            "like_count": 0,
            "dislike_count": 0,
            "comment_count": 0,
            "scrap_count": 0,
            "created_at": datetime.utcnow()
        })
        post_id = inserted_post.inserted_id  # ✅ inserted_id 저장
        print(f"✅ 테스트 게시글 추가 완료 (ID: {post_id})")
    else:
        post_id = existing_post["_id"]  # ✅ 기존 ObjectId 유지

    # ✅ 기본 댓글 추가 (수정된 부분)
    existing_comment = await comments_collection.find_one({"content": "테스트 댓글"})
    if not existing_comment:
        inserted_comment = await comments_collection.insert_one({
            "post_id": post_id,
            "author_id": user_id,
            "content": "테스트 댓글",
            "like_count": 0,
            "dislike_count": 0,
            "created_at": datetime.utcnow()
        })
        print(f"✅ 테스트 댓글 추가 완료 (ID: {inserted_comment.inserted_id})")
    else:
        print(f"✅ 테스트 댓글 이미 있음 (ID: {existing_comment['_id']})")

    # ✅ 기본 프리셋 추가
    existing_preset = await presets_collection.find_one({"user_id": user_id})
    if not existing_preset:
        preset_id = await presets_collection.insert_one({
            "user_id": user_id,
            "name": "기본 프리셋",
            "categories": [],
            "created_at": datetime.utcnow()
        })
        print(f"✅ 기본 프리셋 추가 완료 (ID: {preset_id.inserted_id})")
    else:
        print(f"✅ 기본 프리셋 이미 있음 (ID: {existing_preset['_id']})")
