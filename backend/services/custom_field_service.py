import uuid

from cryptography.exceptions import InvalidTag as CryptoInvalidTag
from sqlalchemy import and_, delete, select

from backend.models.custom_field import CustomFieldTable, CustomFieldValueTable
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from backend.schemas.custom_field_schema import (
    CustomFieldCreateSchema,
    CustomFieldDefinitionSchema,
    CustomFieldUpdateSchema,
    CustomFieldValueInputSchema,
    CustomFieldValueItemSchema,
    CustomFieldValuesReplaceSchema,
    EntityType,
)

ALLOWED_ENTITY_TYPES: set[str] = {"account", "category", "resource"}


class CustomFieldService:
    """CRUD определений и значений кастомных полей."""

    def __init__(
        self,
        db_repo: DatabaseRepository,
        encrypt_repo: EncryptionRepository,
    ):
        self.db_repo = db_repo
        self.encrypt_repo = encrypt_repo

    def _to_definition(self, field: CustomFieldTable) -> CustomFieldDefinitionSchema:
        return CustomFieldDefinitionSchema(
            id=field.id,
            name=field.name,
            is_required=field.is_required,
            is_secret=field.is_secret,
            order=field.order,
        )

    def _validate_entity_type(self, entity_type: str) -> None:
        if entity_type not in ALLOWED_ENTITY_TYPES:
            raise ValueError(
                f"Недопустимый entity_type: {entity_type}. "
                f"Допустимы: {', '.join(sorted(ALLOWED_ENTITY_TYPES))}"
            )

    async def list_definitions(self) -> list[CustomFieldDefinitionSchema]:
        """Каталог определений для пикера."""
        fields = await self.db_repo.get_list(CustomFieldTable, limit=1000)
        return [self._to_definition(f) for f in fields]

    async def create_definition(
        self,
        data: CustomFieldCreateSchema,
    ) -> CustomFieldDefinitionSchema:
        """Создать определение поля."""
        existing = await self.db_repo.get(
            CustomFieldTable,
            filters={"name": data.name.strip()},
        )
        if existing:
            raise ValueError(f"Поле «{data.name}» уже существует")

        field = CustomFieldTable(
            id=str(uuid.uuid4()),
            name=data.name.strip(),
            is_required=data.is_required,
            is_secret=data.is_secret,
            order=data.order,
        )
        await self.db_repo.add(field)
        return self._to_definition(field)

    async def update_definition(
        self,
        field_id: str,
        data: CustomFieldUpdateSchema,
    ) -> CustomFieldDefinitionSchema:
        """Обновить имя / обязательность / порядок."""
        field = await self.db_repo.get(CustomFieldTable, filters={"id": field_id})
        if not field:
            raise ValueError(f"Поле {field_id} не найдено")

        values: dict = {}
        if data.name is not None:
            name = data.name.strip()
            duplicate = await self.db_repo.get(
                CustomFieldTable,
                filters={"name": name},
            )
            if duplicate and duplicate.id != field_id:
                raise ValueError(f"Поле «{name}» уже существует")
            values["name"] = name
        if data.is_required is not None:
            values["is_required"] = data.is_required
        if data.order is not None:
            values["order"] = data.order

        if values:
            await self.db_repo.update(
                CustomFieldTable,
                filters={"id": field_id},
                values=values,
            )
            field = await self.db_repo.get(CustomFieldTable, filters={"id": field_id})

        return self._to_definition(field)

    async def delete_definition(self, field_id: str) -> None:
        """Удалить определение и все значения."""
        field = await self.db_repo.get(CustomFieldTable, filters={"id": field_id})
        if not field:
            raise ValueError(f"Поле {field_id} не найдено")
        await self.db_repo.delete(field)

    def _decrypt_value(
        self,
        row: CustomFieldValueTable,
        field: CustomFieldTable,
        master_password: str,
    ) -> str:
        if not field.is_secret:
            return row.value or ""
        if not row.encrypted_data or not row.salt or not row.nonce:
            return ""
        try:
            return self.encrypt_repo.decrypt_data(
                row.encrypted_data,
                row.salt,
                row.nonce,
                master_password,
            )
        except CryptoInvalidTag as exc:
            raise ValueError(
                "Ключ не подходит. Проверьте мастер-пароль или настройки итераций."
            ) from exc

    def _encrypt_secret(self, plaintext: str, master_password: str) -> dict:
        enc = self.encrypt_repo.encrypt_data(plaintext, master_password)
        return {
            "value": None,
            "encrypted_data": enc["encrypted_data"],
            "salt": enc["salt"],
            "nonce": enc["nonce"],
        }

    async def get_entity_values(
        self,
        entity_type: EntityType,
        entity_id: str,
        master_password: str,
    ) -> list[CustomFieldValueItemSchema]:
        """Поля сущности с расшифрованными секретами."""
        self._validate_entity_type(entity_type)
        stmt = (
            select(CustomFieldValueTable, CustomFieldTable)
            .join(
                CustomFieldTable,
                CustomFieldValueTable.field_id == CustomFieldTable.id,
            )
            .where(
                and_(
                    CustomFieldValueTable.entity_type == entity_type,
                    CustomFieldValueTable.entity_id == entity_id,
                )
            )
            .order_by(CustomFieldTable.order.asc(), CustomFieldTable.name.asc())
        )
        result = await self.db_repo.session.execute(stmt)
        rows = result.all()

        items: list[CustomFieldValueItemSchema] = []
        for value_row, field in rows:
            items.append(
                CustomFieldValueItemSchema(
                    field_id=field.id,
                    name=field.name,
                    is_required=field.is_required,
                    is_secret=field.is_secret,
                    order=field.order,
                    value=self._decrypt_value(value_row, field, master_password),
                )
            )
        return items

    async def _resolve_field(
        self,
        item: CustomFieldValueInputSchema,
    ) -> CustomFieldTable:
        if item.field_id:
            field = await self.db_repo.get(
                CustomFieldTable,
                filters={"id": item.field_id},
            )
            if not field:
                raise ValueError(f"Поле {item.field_id} не найдено")
            return field

        assert item.new_field is not None
        created = await self.create_definition(
            CustomFieldCreateSchema(
                name=item.new_field.name,
                is_required=item.new_field.is_required,
                is_secret=item.new_field.is_secret,
                order=item.new_field.order,
            )
        )
        field = await self.db_repo.get(CustomFieldTable, filters={"id": created.id})
        assert field is not None
        return field

    async def replace_entity_values(
        self,
        entity_type: EntityType,
        entity_id: str,
        payload: CustomFieldValuesReplaceSchema,
        master_password: str,
    ) -> list[CustomFieldValueItemSchema]:
        """Атомарно заменить набор полей сущности."""
        self._validate_entity_type(entity_type)

        resolved: list[tuple[CustomFieldTable, str]] = []
        seen_field_ids: set[str] = set()

        for item in payload.fields:
            field = await self._resolve_field(item)
            if field.id in seen_field_ids:
                raise ValueError(f"Поле «{field.name}» указано дважды")
            seen_field_ids.add(field.id)

            value = item.value if item.value is not None else ""
            if field.is_required and not str(value).strip():
                raise ValueError(f"Поле «{field.name}» обязательно")
            resolved.append((field, str(value)))

        await self.db_repo.session.execute(
            delete(CustomFieldValueTable).where(
                and_(
                    CustomFieldValueTable.entity_type == entity_type,
                    CustomFieldValueTable.entity_id == entity_id,
                )
            )
        )

        for field, value in resolved:
            if field.is_secret:
                enc_fields = self._encrypt_secret(value, master_password)
                row = CustomFieldValueTable(
                    id=str(uuid.uuid4()),
                    field_id=field.id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    **enc_fields,
                )
            else:
                row = CustomFieldValueTable(
                    id=str(uuid.uuid4()),
                    field_id=field.id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    value=value,
                    encrypted_data=None,
                    salt=None,
                    nonce=None,
                )
            self.db_repo.session.add(row)

        await self.db_repo.session.commit()
        return await self.get_entity_values(entity_type, entity_id, master_password)

    async def delete_values_for_entity(
        self,
        entity_type: EntityType,
        entity_id: str,
    ) -> None:
        """Удалить все значения при удалении сущности."""
        self._validate_entity_type(entity_type)
        await self.db_repo.session.execute(
            delete(CustomFieldValueTable).where(
                and_(
                    CustomFieldValueTable.entity_type == entity_type,
                    CustomFieldValueTable.entity_id == entity_id,
                )
            )
        )
        await self.db_repo.session.commit()
