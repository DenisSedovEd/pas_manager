"""Одноразовый перенос данных из SQLite в PostgreSQL.

Запускать после старта сервиса (Alembic + init_db):

    python -m scripts.migrate_sqlite_to_postgres
    python -m scripts.migrate_sqlite_to_postgres --sqlite data/accounts.sqlite
    python -m scripts.migrate_sqlite_to_postgres --force
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from collections.abc import Iterable, Sequence
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from backend.core.config import BASE_DIR, settings

TABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "categories": (
        "id",
        "category_name",
        "description",
        "icon",
        "order",
        "parent_id",
    ),
    "resources": ("id", "resource_name", "description", "icon"),
    "accounts": (
        "id",
        "category_id",
        "resource_id",
        "login",
        "email",
        "phone",
        "order",
        "label",
        "encrypted_data",
        "salt",
        "nonce",
        "tag",
    ),
    "app_settings": (
        "id",
        "master_password_hash",
        "encrypted_master_password",
        "bio_enc_data",
    ),
    "custom_icons": (
        "id",
        "label",
        "filename",
        "content_type",
        "fallback_emoji",
        "created_at",
    ),
}

SEQUENCE_TABLES = ("accounts",)


def _quote_ident(name: str) -> str:
    return f'"{name}"'


def _table_exists(sqlite_conn: sqlite3.Connection, table: str) -> bool:
    row = sqlite_conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def _fetch_rows(
    sqlite_conn: sqlite3.Connection,
    table: str,
    columns: Sequence[str],
) -> list[dict]:
    cols_sql = ", ".join(_quote_ident(c) for c in columns)
    cur = sqlite_conn.execute(f"SELECT {cols_sql} FROM {_quote_ident(table)}")
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row, strict=True)) for row in cur.fetchall()]


def _sort_categories(rows: list[dict]) -> list[dict]:
    """Родители раньше детей (self-FK parent_id)."""
    normalized = []
    for row in rows:
        item = dict(row)
        item["parent_id"] = _blank_to_none(item.get("parent_id"))
        normalized.append(item)

    by_id = {row["id"]: row for row in normalized}
    children: dict[str | None, list[dict]] = defaultdict(list)
    for row in normalized:
        parent_id = row.get("parent_id")
        if parent_id and parent_id not in by_id:
            raise ValueError(
                f"Категория {row['id']}: parent_id={parent_id} отсутствует в SQLite"
            )
        children[parent_id].append(row)

    ordered: list[dict] = []

    def walk(parent_id: str | None) -> None:
        for row in children.get(parent_id, []):
            ordered.append(row)
            walk(row["id"])

    walk(None)
    if len(ordered) != len(normalized):
        raise ValueError("Обнаружен цикл в parent_id категорий")
    return ordered


def _blank_to_none(value: object) -> object:
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _default_category_id(categories: Sequence[dict]) -> str:
    """id корневой категории Other (fallback для битых category_id)."""
    for row in categories:
        if row.get("category_name") == "Other" and not row.get("parent_id"):
            return str(row["id"])
    for row in categories:
        if not row.get("parent_id"):
            return str(row["id"])
    raise ValueError("В SQLite нет категории для подстановки пустого category_id")


def _normalize_row(
    table: str,
    row: dict,
    *,
    default_category_id: str | None = None,
) -> dict:
    data = {key: _blank_to_none(value) for key, value in row.items()}

    if table == "categories":
        data["parent_id"] = _blank_to_none(data.get("parent_id"))

    if table == "accounts":
        data["resource_id"] = _blank_to_none(data.get("resource_id"))
        if not data.get("category_id"):
            if not default_category_id:
                raise ValueError(
                    f"Account id={data.get('id')}: пустой category_id, "
                    "дефолтная категория не найдена"
                )
            data["category_id"] = default_category_id

    if table == "app_settings" and data.get("bio_enc_data") is not None:
        value = data["bio_enc_data"]
        if isinstance(value, str | bytes | bytearray):
            data["bio_enc_data"] = json.loads(value)
    return data


def _insert_rows(
    pg_conn: Connection,
    table: str,
    columns: Sequence[str],
    rows: Iterable[dict],
    *,
    default_category_id: str | None = None,
) -> int:
    cols_sql = ", ".join(_quote_ident(c) for c in columns)
    placeholders = ", ".join(f":{c}" for c in columns)
    stmt = text(
        f"INSERT INTO {_quote_ident(table)} ({cols_sql}) "
        f"VALUES ({placeholders})"
    )
    count = 0
    remapped = 0
    for row in rows:
        if (
            table == "accounts"
            and default_category_id
            and not _blank_to_none(row.get("category_id"))
        ):
            remapped += 1
        pg_conn.execute(
            stmt,
            _normalize_row(
                table,
                row,
                default_category_id=default_category_id,
            ),
        )
        count += 1
    if remapped:
        print(
            f"warn  {table}: {remapped} строк с пустым category_id "
            f"→ {default_category_id}"
        )
    return count


def _reset_sequences(pg_conn: Connection) -> None:
    for table in SEQUENCE_TABLES:
        max_id = pg_conn.execute(
            text(f"SELECT MAX(id) FROM {_quote_ident(table)}")
        ).scalar()
        if max_id is None:
            continue
        pg_conn.execute(
            text(
                "SELECT setval("
                f"pg_get_serial_sequence('{table}', 'id'), :max_id)"
            ),
            {"max_id": max_id},
        )


def _count(pg_conn: Connection, table: str) -> int:
    return pg_conn.execute(
        text(f"SELECT COUNT(*) FROM {_quote_ident(table)}")
    ).scalar_one()


def _prepare_target(pg_conn: Connection, *, force: bool) -> None:
    """Очистить Postgres перед копированием.

    init_db после старта всегда создаёт категорию Other — без wipe перенос
    невозможен. Если уже есть accounts/app_settings — нужен --force.
    """
    accounts = _count(pg_conn, "accounts")
    settings_rows = _count(pg_conn, "app_settings")
    if (accounts or settings_rows) and not force:
        raise RuntimeError(
            "В PostgreSQL уже есть данные "
            f"(accounts={accounts}, app_settings={settings_rows}). "
            "Перезапустите с --force, если нужно полностью заменить их из SQLite."
        )

    tables_sql = ", ".join(_quote_ident(t) for t in TABLE_COLUMNS)
    pg_conn.execute(text(f"TRUNCATE {tables_sql} RESTART IDENTITY CASCADE"))
    print("wipe  target tables")


def migrate(sqlite_path: Path, engine: Engine, *, force: bool = False) -> None:
    """Скопировать данные из SQLite в PostgreSQL."""
    if not sqlite_path.is_file():
        raise FileNotFoundError(f"SQLite-файл не найден: {sqlite_path}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    try:
        with engine.begin() as pg_conn:
            _prepare_target(pg_conn, force=force)

            default_category_id: str | None = None
            for table, columns in TABLE_COLUMNS.items():
                if not _table_exists(sqlite_conn, table):
                    print(f"skip  {table}: нет в SQLite")
                    continue

                rows = _fetch_rows(sqlite_conn, table, columns)
                if table == "categories":
                    rows = _sort_categories(rows)
                    default_category_id = _default_category_id(rows)

                inserted = _insert_rows(
                    pg_conn,
                    table,
                    columns,
                    rows,
                    default_category_id=default_category_id,
                )
                print(f"ok    {table}: {inserted}")

            _reset_sequences(pg_conn)
    finally:
        sqlite_conn.close()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Одноразовый перенос SQLite → PostgreSQL",
    )
    parser.add_argument(
        "--sqlite",
        type=Path,
        default=None,
        help="Путь к SQLite-файлу (по умолчанию data/<DB__SQLITE_PATH>)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Очистить Postgres даже если там уже есть accounts/app_settings",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Точка входа CLI."""
    args = parse_args(argv)
    sqlite_path = args.sqlite or (BASE_DIR / "data" / settings.db.sqlite_path)
    engine = create_engine(settings.db.sync_url)

    print(f"source: {sqlite_path}")
    print(f"target: {settings.db.host}:{settings.db.port}/{settings.db.name}")
    migrate(sqlite_path, engine, force=args.force)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
