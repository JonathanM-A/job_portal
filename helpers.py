from flask import request

def check_required_fields(required_fields):
    data = request.get_json()
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return False, missing_fields
    return True, None


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["pdf", "doc", "docx"]
