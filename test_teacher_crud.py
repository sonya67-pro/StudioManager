"""Проверка CRUD-операций через TeacherRepository."""
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.teacher_repo import TeacherRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория преподавателей."""
    init_db()
    print("=== Проверка CRUD преподавателей ===\n")

    with get_session() as session:
        repo = TeacherRepository(session)

        # CREATE
        print("1. Добавляем трёх преподавателей...")
        ivanova = repo.add(
            "Иванова Мария Петровна",
            rate=Decimal("1000.00"),
            commission_percent=Decimal("30.00"),
        )
        petrov = repo.add(
            "Петров Сергей Иванович",
            rate=Decimal("1200.00"),
            commission_percent=Decimal("25.00"),
        )
        sidorova = repo.add(
            "Сидорова Анна Викторовна",
            rate=Decimal("900.00"),
        )
        print(f"   Создано: {ivanova.full_name}, "
              f"{petrov.full_name}, {sidorova.full_name}\n")

        # READ (все)
        print("2. Список всех преподавателей:")
        for teacher in repo.list_all():
            print(f"   [{teacher.id}] {teacher.full_name} — "
                  f"ставка {teacher.rate} ₽, комиссия {teacher.commission_percent}%")
        print()

        # READ (поиск)
        print("3. Поиск по 'петров':")
        for teacher in repo.find_by_name("петров"):
            print(f"   [{teacher.id}] {teacher.full_name}")
        print()

        # UPDATE (ставка и комиссия)
        print("4. Меняем ставку Ивановой: 1500 ₽, комиссия 35%...")
        ivanova = repo.update_rate(
            ivanova.id,
            rate=Decimal("1500.00"),
            commission_percent=Decimal("35.00"),
        )
        print(f"   Новая ставка: {ivanova.rate} ₽, "
              f"комиссия: {ivanova.commission_percent}%\n")

        # DELETE
        print("5. Удаляем Петрова...")
        deleted = repo.delete(petrov.id)
        print(f"   Удалён: {deleted}\n")

        print("6. Итоговый список:")
        for teacher in repo.list_all():
            print(f"   [{teacher.id}] {teacher.full_name} — "
                  f"ставка {teacher.rate} ₽, комиссия {teacher.commission_percent}%")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
