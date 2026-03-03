from pydantic import BaseModel, Field

class AccountBaseSchema(BaseModel):
    platform: str = Field(
        description="Platform name",
    )
    user_name: str = Field(
        description="Username",
    )
    password: str = Field(
        description="Password",
    )


class AccountRequestSchema(AccountBaseSchema):
    pass

class AccountResponseSchema(AccountBaseSchema):
    pass