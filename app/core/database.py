from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["safari_db"]

# ✅ 컬렉션 생성 (존재하지 않으면 자동 생성됨)
users_collection = db["users"]
posts_collection = db["posts"]
comments_collection = db["comments"]
categories_collection = db["categories"]
programs_collection = db["programs"]

async def initialize_database():
    """DB 초기화 및 컬렉션 생성"""
    existing_collections = await db.list_collection_names()

    if "posts" not in existing_collections:
        await db.create_collection("posts")
        print("✅ posts 컬렉션 생성 완료")

    if "comments" not in existing_collections:
        await db.create_collection("comments")
        print("✅ comments 컬렉션 생성 완료")

    # ✅ 테스트용 더미 데이터 추가 (게시글)
    dummy_post = {
        "title": "테스트 게시글",
        "content": "MongoDB 초기화 테스트 중",
        "author": "testuser@example.com",
        "created_at": "2024-02-10T12:00:00",
        "likes": 0,
        "dislikes": 0,
        "views": 0
    }

    if not await posts_collection.find_one({"title": "테스트 게시글"}):
        await posts_collection.insert_one(dummy_post)
        print("✅ 더미 게시글 추가 완료")
