"""Проверка CRUD-операций через PaymentRepository."""
from datetime import date
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.payment_repo import PaymentRepository
from src.repositories.student_repo import StudentRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория платежей."""
    init_db()
    print("=== Проверка CRUD платежей ===\n")

    with get_session() as session:
        students = StudentRepository(session)
        payments = PaymentRepository(session)

        print("0. Подготовка: создаём двух учеников...")
        ivanov = students.add("Иванов Иван Иванович")
        petrov = students.add("Петров Пётр Петрович")
        print(f"   Создано: {ivanov.full_name}, {petrov.full_name}\n")

        print("1. Добавляем платежи Иванову...")
        p1 = payments.add(
            student_id=ivanov.id,
            amount=Decimal("5000.00"),
            payment_date=date(2026, 10, 1),
        )
        p2 = payments.add(
            student_id=ivanov.id,
            amount=Decimal("3000.00"),
            payment_date=date(2026, 10, 8),
        )
        print(f"   Платёж 1: {p1.amount} ₽ от {p1.date}")
        print(f"   Платёж 2: {p2.amount} ₽ от {p2.date}\n")

        print("2. Добавляем платёж Петрову...")
        p3 = payments.add(
            student_id=petrov.id,
            amount=Decimal("2000.00"),
        )
        print(f"   Платёж 3: {p3.amount} ₽ от {p3.date}\n")

        print("3. Все платежи:")
        for payment in payments.list_all():
            print(f"   [{payment.id}] {payment.date} — "
                  f"{payment.amount} ₽ (student_id={payment.student_id})")
        print()

        print(f"4. Платежи Иванова (id={ivanov.id}):")
        ivanov_payments = payments.list_by_student(ivanov.id)
        total = Decimal("0.00")
        for payment in ivanov_payments:
            print(f"   [{payment.id}] {payment.date} — {payment.amount} ₽")
            total += payment.amount
        print(f"   Итого: {total} ₽\n")

        print("5. Пытаемся добавить платёж с отрицательной суммой...")
        try:
            payments.add(student_id=ivanov.id, amount=Decimal("-100.00"))
            print("   ОШИБКА: должна была быть ошибка!\n")
        except ValueError as e:
            print(f"   ✓ Ошибка перехвачена: {e}\n")

        print("6. Удаляем платёж №1...")
        deleted = payments.delete(p1.id)
        print(f"   Удалён: {deleted}\n")

        print("7. Итоговый список платежей:")
        for payment in payments.list_all():
            print(f"   [{payment.id}] {payment.date} — "
                  f"{payment.amount} ₽ (student_id={payment.student_id})")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
