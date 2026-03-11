from pydantic import BaseModel


class BioUnlockRequest(BaseModel):
    bio_token: str