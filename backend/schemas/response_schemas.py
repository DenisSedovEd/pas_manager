from pydantic import BaseModel


class SuccessResponse(BaseModel):
    ok: bool = True

class MessageResponse(BaseModel):
    ok: bool = True
    message: str