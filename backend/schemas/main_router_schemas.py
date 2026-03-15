from pydantic import BaseModel


class UnlockRequest(BaseModel):
    master_password: str


class StatusResponse(BaseModel):
    user_id: int
    is_unlocked: bool


class SuccessResponse(BaseModel):
    status: str
    ok: bool


class BiometricRequest(BaseModel):
    bio_token: str


class EnableBiometricRequest(BaseModel):
    encrypted_master_password: str
    bio_enc_data: dict


class LogoutRequest(BaseModel):
    init_data: str