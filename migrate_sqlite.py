
import asyncio
import sqlite3
from pathlib import Path

from sqlalchemy import text
from src.db import engine

BASE_DIR = Path(__file__).resolve().parent

DATABASES = {
    "pages.db": "pages",
    "photos.db": "photos",
    "users.db": "user",
    "email_req.db": "contact",
}


def read_sqlite(database_path: Path, table: str) -> list[dict]:
    with sqlite3.connect(database_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
        return [dict(row) for row in rows]


async def main():
    data = {}

    for filename, table in DATABASES.items():
        path = BASE_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"Не найдена база: {path}")

        rows = read_sqlite(path, table)

        if table == "user":
            for row in rows:
                for column in ("is_active", "is_superuser", "is_verified"):
                    row[column] = bool(row[column])

        data[table] = rows
        print(f"{filename}: найдено {len(rows)} записей")

    try:
        async with engine.begin() as conn:
            # Сначала проверяем все таблицы: они должны быть пустыми.
            for table, rows in data.items():
                if not rows:
                    continue

                result = await conn.execute(
                    text(f'SELECT COUNT(*) FROM "{table}"')
                )
                count = result.scalar_one()

                if count != 0:
                    raise RuntimeError(
                        f"Таблица {table} уже содержит {count} записей. "
                        "Перенос отменён, данные не изменены."
                    )

            # Вставляем все записи в одной транзакции.
            for table, rows in data.items():
                for row in rows:
                    columns = list(row.keys())
                    column_sql = ", ".join(
                        f'"{column}"' for column in columns
                    )
                    values_sql = ", ".join(
                        f":{column}" for column in columns
                    )

                    await conn.execute(
                        text(
                            f'INSERT INTO "{table}" '
                            f"({column_sql}) VALUES ({values_sql})"
                        ),
                        row,
                    )

                print(f"{table}: подготовлено {len(rows)} записей")

        print("Перенос успешно завершён.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
