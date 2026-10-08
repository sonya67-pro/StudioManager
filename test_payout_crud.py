"""Проверка CRUD-операций через PayoutRepository."""
from datetime import date
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.payout_repo import PayoutRepository
from src.repositories.teacher_repo import TeacherRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория выплат."""
    init_db()
    print("=== Проверка CRUD выплат ===\n")

    with get_session() as session:
        teachers = TeacherRepository(session)
        payouts = PayoutRepository(session)

        print("0. Подготовка: создаём двух преподавателей...")
        ivanova = teachers.add(
            "Иванова Мария Петровна",
            rate=Decimal("1000.00"),
            commission_percent=Decimal("30.00"),
        )
        petrov = teachers.add(
            "Петров Сергей Иванович",
            rate=Decimal("1200.00"),
            commission_percent=Decimal("25.00"),
        )
        print(f"   Создано: {ivanova.full_name}, {petrov.full_name}\n")

        print("1. Создаём выплату Ивановой за октябрь 2026...")
        p1 = payouts.add(
            teacher_id=ivanova.id,
            amount=Decimal("15000.00"),
            period_start=date(2026, 10, 1),
            period_end=date(2026, 10, 31),
        )
        print(f"   Выплата 1: {p1.amount} ₽\n")

        print("2. Создаём вторую выплату Ивановой за сентябрь 2026...")
        p2 = payouts.add(
            teacher_id=ivanova.id,
            amount=Decimal("12000.00"),
            period_start=date(2026, 9, 1),
            period_end=date(2026, 9, 30),
        )
        print(f"   Выплата 2: {p2.amount} ₽\n")

        print("3. Создаём выплату Петрову за октябрь 2026...")
        p3 = payouts.add(
            teacher_id=petrov.id,
            amount=Decimal("10000.00"),
            period_start=date(2026, 10, 1),
            period_end=date(2026, 10, 31),
        )
        print(f"   Выплата 3: {p3.amount} ₽\n")

        print("4. Все выплаты:")
        for payout in payouts.list_all():
            status = "оплачено" if payout.is_paid else "не оплачено"
            print(f"   [{payout.id}] {payout.amount} ₽ — {status}")
        print()

        print(f"5. Выплаты Ивановой (id={ivanova.id}):")
        for payout in payouts.list_by_teacher(ivanova.id):
            status = "оплачено" if payout.is_paid else "не оплачено"
            print(f"   [{payout.id}] {payout.amount} ₽ — {status}")
        print()

        print("6. Неоплаченные выплаты:")
        for payout in payouts.list_unpaid():
            print(f"   [{payout.id}] {payout.amount} ₽")
        print()

        print("7. Отмечаем выплату №1 как оплаченную...")
        p1 = payouts.mark_paid(p1.id)
        print(f"   Статус: is_paid={p1.is_paid}\n")

        print("8. Неоплаченные выплаты после отметки:")
        for payout in payouts.list_unpaid():
            print(f"   [{payout.id}] {payout.amount} ₽")
        print()

        print("9. Пытаемся создать выплату с некорректным периодом...")
        try:
            payouts.add(
                teacher_id=ivanova.id,
                amount=Decimal("5000.00"),
                period_start=date(2026, 10, 31),
                period_end=date(2026, 10, 1),
            )
            print("   ОШИБКА: должна была быть ошибка!\n")
        except ValueError as e:
            print(f"   ✓ Ошибка перехвачена: {e}\n")

        print("10. Удаляем выплату №3...")
        deleted = payouts.delete(p3.id)
        print(f"   Удалено: {deleted}\n")

        print("11. Итоговый список:")
        for payout in payouts.list_all():
            status = "оплачено" if payout.is_paid else "не оплачено"
            print(f"   [{payout.id}] {payout.amount} ₽ — {status}")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
