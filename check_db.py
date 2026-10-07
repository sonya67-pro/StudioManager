"""Проверка структуры базы данных StudioManager."""
import sqlite3


def main() -> None:
    """Выводит список таблиц в базе данных."""
    connection = sqlite3.connect("studio.db")
    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    connection.close()

    print("Таблицы в базе данных:")
    for table in tables:
        print(f"  - {table}")


if __name__ == "__main__":
    main()