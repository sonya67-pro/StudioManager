"""Проверка бизнес-логики FinanceService."""
from datetime import date, time
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.lesson_repo import LessonRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.teacher_repo import TeacherRepository
from src.services.finance_service import FinanceService


def main() -> None:
    """Демонстрирует работу FinanceService."""
    init_db()
    print("=== Проверка FinanceService ===\n")

    with get_session() as session:
        students = StudentRepository(session)
        teachers = TeacherRepository(session)
        rooms = RoomRepository(session)
        lessons = LessonRepository(session)
        finance = FinanceService(session)

        print("0. Подготовка данных...")
        ivanov = students.add("Иванов Иван Иванович")
        petrov = students.add("Петров Пётр Петрович")
        teacher = teachers.add(
            "Иванова Мария Петровна",
            rate=Decimal("1000.00"),
            commission_percent=Decimal("30.00"),
        )
        room = rooms.add("Кабинет №1", capacity=4)
        print(f"   Ученики: {ivanov.full_name}, {petrov.full_name}")
        print(f"   Преподаватель: {teacher.full_name}\n")

        print("1. Пополняем баланс Иванова на 5000 ₽ (FR-03)...")
        balance = finance.top_up_balance(ivanov.id, Decimal("5000.00"))
        print(f"   Баланс Иванова: {balance} ₽\n")

        print("2. Пополняем баланс Петрова на 3000 ₽...")
        balance = finance.top_up_balance(petrov.id, Decimal("3000.00"))
        print(f"   Баланс Петрова: {balance} ₽\n")

        print("3. Списываем 1500 ₽ за занятие с Иванова (FR-04)...")
        balance = finance.charge_lesson(ivanov.id, Decimal("1500.00"))
        print(f"   Баланс Иванова: {balance} ₽\n")

        print("4. Пытаемся списать слишком много...")
        try:
            finance.charge_lesson(petrov.id, Decimal("99999.00"))
            print("   ОШИБКА: должна была быть ошибка!\n")
        except ValueError as e:
            print(f"   ✓ Ошибка перехвачена: {e}\n")

        print("5. Список должников (FR-05)...")
        debtors = finance.get_debtors()
        if debtors:
            for sid, name, bal in debtors:
                print(f"   [{sid}] {name} — баланс {bal} ₽")
        else:
            print("   Должников нет")
        print()

        print("6. Создаём 3 занятия для преподавателя (done)...")
        for i, day in enumerate([10, 12, 15], start=1):
            lesson = lessons.add(
                teacher_id=teacher.id,
                room_id=room.id,
                lesson_date=date(2026, 10, day),
                time_start=time(10, 0),
                time_end=time(11, 0),
                cost=Decimal("1000.00"),
                is_group=False,
            )
            lessons.mark_done(lesson.id)
        print("   3 занятия созданы и отмечены как 'done'\n")

        print("7. Считаем комиссию за октябрь 2026 (FR-15)...")
        commission = finance.calc_teacher_commission(
            teacher_id=teacher.id,
            period_start=date(2026, 10, 1),
            period_end=date(2026, 10, 31),
        )
        print(f"   Комиссия: {commission} ₽")
        print("   (ожидалось: 3 занятия × 1000 ₽ × 30% = 900 ₽)\n")

        print("8. Создаём ведомость выплаты (FR-16)...")
        payout_id = finance.create_payout(
            teacher_id=teacher.id,
            period_start=date(2026, 10, 1),
            period_end=date(2026, 10, 31),
        )
        print(f"   Ведомость создана: id={payout_id}\n")

        print("9. Проверяем статус ведомости...")
        from src.repositories.payout_repo import PayoutRepository

        payouts = PayoutRepository(session)
        payout = payouts.get(payout_id)
        print(f"   Сумма: {payout.amount} ₽")
        print(f"   Оплачено: {bool(payout.is_paid)}\n")

    print("=== Проверка завершена ===")


if __name__ == "__main__":
    main()
