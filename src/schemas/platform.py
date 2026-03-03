from typing import List

from pydantic import BaseModel, Field

from src.models.account import Account


class PlatformBaseSchema(BaseModel):
    name: str = Field(
        description="Platform name",
    )

class PlatformRequestSchema(PlatformBaseSchema):
    pass

class PlatformResponseSchema(PlatformBaseSchema):
    accounts: List[Account] = Field(
        description="Platform accounts",
    )
