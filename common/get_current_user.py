from fastapi import Header

# 임시 current_user Dependency (실제 서비스에서는 JWT에서 파싱)
def get_current_user(
    x_user_id: str = Header(...), 
    x_user_type: str = Header(...)
):
    return {"user_id": x_user_id, "user_type": x_user_type}
