from app.core.database import programs_collection
from bson import ObjectId, errors, Optional
from app.core.utils import convert_objectid

async def create_program(name: str, category_id: str, created_by: str):
    """프로그램 생성"""
    program = {"name": name, "category_id": category_id, "created_by": created_by}
    result = await programs_collection.insert_one(program)
    return str(result.inserted_id)

async def get_programs(category_id: str = None):
    """모든 프로그램 조회"""
    query = {"category_id": category_id} if category_id else {}
    programs = await programs_collection.find(query).to_list(100)

    # ✅ ObjectId를 문자열로 변환 후 반환
    return [
        {
            "id": str(program["_id"]),  # ObjectId -> str 변환
            "name": program["name"],
            "category_id": str(program["category_id"]) if program.get("category_id") else None
        }
        for program in programs
    ]


async def get_program(program_id: str):
    """특정 프로그램 조회"""
    try:
        obj_id = ObjectId(program_id)
    except errors.InvalidId:
        return None

    program = await programs_collection.find_one({"_id": obj_id})
    if not program:
        return None

    return {
        "id": str(program["_id"]),
        "name": program["name"],
        "category_id": str(program["category_id"]) if program.get("category_id") else None
    }


from app.core.database import programs_collection
from bson import ObjectId, errors, Optional
from app.core.utils import convert_objectid

async def create_program(name: str, category_id: str, created_by: str):
    """프로그램 생성"""
    program = {"name": name, "category_id": category_id, "created_by": created_by}
    result = await programs_collection.insert_one(program)
    return str(result.inserted_id)

async def get_programs(category_id: str = None):
    """모든 프로그램 조회"""
    query = {"category_id": category_id} if category_id else {}
    programs = await programs_collection.find(query).to_list(100)

    # ✅ ObjectId를 문자열로 변환 후 반환
    return [
        {
            "id": str(program["_id"]),  # ObjectId -> str 변환
            "name": program["name"],
            "category_id": str(program["category_id"]) if program.get("category_id") else None
        }
        for program in programs
    ]


async def get_program(program_id: str):
    """특정 프로그램 조회"""
    try:
        obj_id = ObjectId(program_id)
    except errors.InvalidId:
        return None

    program = await programs_collection.find_one({"_id": obj_id})
    if not program:
        return None

    return {
        "id": str(program["_id"]),
        "name": program["name"],
        "category_id": str(program["category_id"]) if program.get("category_id") else None
    }


async def update_program(program_id: str, new_name: str, new_category_id: Optional[str]):
    """프로그램 정보 수정"""
    obj_id = ObjectId(program_id)
    update_fields = {}

    if new_name:
        update_fields["name"] = new_name
    if new_category_id:
        update_fields["category_id"] = new_category_id

    if update_fields:
        await programs_collection.update_one({"_id": obj_id}, {"$set": update_fields})

    updated_program = await programs_collection.find_one({"_id": obj_id})
    return convert_objectid(updated_program)  # ✅ 변환 적용하여 `id` 필드 반환

async def delete_program(program_id: str):
    """프로그램 삭제"""
    obj_id = ObjectId(program_id)
    await programs_collection.delete_one({"_id": obj_id})


async def delete_program(program_id: str):
    """프로그램 삭제"""
    obj_id = ObjectId(program_id)
    await programs_collection.delete_one({"_id": obj_id})
