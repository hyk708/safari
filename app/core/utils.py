from bson import ObjectId
from datetime import datetime

def convert_objectid(data):
    """MongoDB의 ObjectId 및 datetime을 문자열로 변환하는 함수"""
    
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]

    if isinstance(data, dict):
        return {key if key != "_id" else "id": convert_objectid(value) for key, value in data.items()}  # ✅ `dict comprehension` 최적화

    if isinstance(data, ObjectId):
        return str(data)  # ✅ ObjectId → 문자열 변환

    if isinstance(data, datetime):
        return data.isoformat()  # ✅ datetime → ISO 8601 문자열 변환 (예: "2024-02-10T12:00:00")

    return data

