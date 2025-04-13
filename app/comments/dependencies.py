from fastapi import Request


# no jwt implementation yet
def get_user_id(request: Request):
    user_id = getattr(request.state, "user_id", None)
    return user_id
