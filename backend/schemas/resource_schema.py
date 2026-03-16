from typing import Optional

from pydantic import Field, BaseModel


class ResourceBaseSchema(BaseModel):
    resource_name: str = Field(description="Resource name")
    description: Optional[str] = Field(
        default=None,
        description="Description",
    )
    icon: Optional[str] = Field(
        default=None,
        description="Icon",
    )


class ResourceResponseSchema(ResourceBaseSchema):
    id: str


class ResourceRequestSchema(ResourceBaseSchema):
    pass
