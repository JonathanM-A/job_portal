import redis
from flask import request
from app import jwt


def check_required_fields(required_fields):
    """Checks if all required fields are provided"""
    data = request.get_json()
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, missing_fields
    return True, None


def allowed_file(filename):
    """Checks if file type is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["pdf", "doc", "docx"]

jwt_redis_blocklist = redis.Redis(
    host="localhost", port=6379, db=0, decode_responses=True
)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None