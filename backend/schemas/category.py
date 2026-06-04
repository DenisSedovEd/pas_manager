from pydantic import BaseModel, Field
from typing import Optional


class CategoryResponseSchema(BaseModel):
    """Категория с количеством аккаунтов и подкатегорий"""
    id: str
    name: str = Field(description="Category name")
    icon: Optional[str] = Field(default=None, description="Category icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
    order: int
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    accounts_count: int = Field(description="Number of accounts in this category")
    children_count: int = Field(default=0, description="Number of subcategories")


class CategoryRequestSchema(BaseModel):
    """Для создания/обновления категории"""
    name: str = Field(description="Category name")
    icon: str = Field(description="Category icon/emoji")
    description: Optional[str] = Field(default=None, description="Description")
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
