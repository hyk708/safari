from bson import ObjectId

def convert_objectid(data):
    """MongoDB의 ObjectId를 문자열로 변환하는 함수"""
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    if isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    return data
