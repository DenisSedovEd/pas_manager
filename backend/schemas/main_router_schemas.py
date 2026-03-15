from pydantic import BaseModel


class UnlockRequest(BaseModel):
    master_password: str


class StatusResponse(BaseModel):
    user_id: int
    is_unlocked: bool


class BiometricRequest(BaseModel):
    bio_token: str
