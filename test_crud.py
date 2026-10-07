"""Проверка CRUD-операций через StudentRepository."""
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.student_repo import StudentRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория учеников."""
    init_db()
    print("=== Проверка CRUD учеников ===\n")

    with get_session() as session:
        repo = StudentRepository(session)

        # CREATE
        print("1. Добавляем трёх учеников...")
        ivanov = repo.add("Иванов Иван Иванович", "+7-900-111-11-11")
        petrov = repo.add("Петров Пётр Петрович", "+7-900-222-22-22")
        sidorov = repo.add("Сидоров Сидор Сидорович")
        print(f"   Создано: {ivanov.full_name}, "
              f"{petrov.full_name}, {sidorov.full_name}")

        # READ (все)
        print("2. Список всех учеников:")
        for student in repo.list_all():
            print(f"   [{student.id}] {student.full_name} — баланс {student.balance} ₽")
        print()

        # READ (поиск)
        print("3. Поиск по 'петр':")
        for student in repo.find_by_name("петр"):
            print(f"   [{student.id}] {student.full_name}")
        print()

        # UPDATE (баланс)
        print("4. Пополняем баланс Иванова на 5000 ₽...")
        ivanov = repo.update_balance(ivanov.id, Decimal("5000.00"))
        print(f"   Новый баланс: {ivanov.balance} ₽\n")

        print("5. Списываем 1500 ₽ с Иванова...")
        ivanov = repo.update_balance(ivanov.id, Decimal("-1500.00"))
        print(f"   Новый баланс: {ivanov.balance} ₽\n")

        # DELETE
        print("6. Удаляем Петрова...")
        deleted = repo.delete(petrov.id)
        print(f"   Удалён: {deleted}\n")

        print("7. Итоговый список:")
        for student in repo.list_all():
            print(f"   [{student.id}] {student.full_name} — баланс {student.balance} ₽")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
