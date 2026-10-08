"""Проверка ScheduleService — конфликты расписания."""
from datetime import date, time
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.lesson_repo import LessonRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.teacher_repo import TeacherRepository
from src.services.schedule_service import ScheduleService


def main() -> None:
    """Демонстрирует работу ScheduleService."""
    init_db()
    print("=== Проверка ScheduleService ===\n")

    with get_session() as session:
        teachers = TeacherRepository(session)
        rooms = RoomRepository(session)
        lessons = LessonRepository(session)
        schedule = ScheduleService(session)

        print("0. Подготовка данных...")
        teacher = teachers.add(
            "Иванова Мария Петровна",
            rate=Decimal("1000.00"),
            commission_percent=Decimal("30.00"),
        )
        room_1 = rooms.add("Кабинет №1", capacity=2)
        room_2 = rooms.add("Кабинет №2", capacity=1)
        print(f"   Преподаватель: {teacher.full_name}")
        print(f"   Кабинеты: {room_1.name}, {room_2.name}\n")

        test_date = date(2026, 10, 15)

        print("1. Создаём занятие с 10:00 до 11:00 в кабинете №1...")
        lesson_1 = lessons.add(
            teacher_id=teacher.id,
            room_id=room_1.id,
            lesson_date=test_date,
            time_start=time(10, 0),
            time_end=time(11, 0),
            cost=Decimal("1000.00"),
        )
        print(f"   Занятие id={lesson_1.id} создано\n")

        print("2. Проверяем конфликт кабинета №1 в 10:30–11:30...")
        conflicts = schedule.check_room_conflict(
            room_id=room_1.id,
            lesson_date=test_date,
            time_start=time(10, 30),
            time_end=time(11, 30),
        )
        print(f"   Найдено конфликтов: {len(conflicts)}")
        for c in conflicts:
            print(f"     [{c.id}] {c.time_start}–{c.time_end}")
        print()

        print("3. Проверяем кабинет №2 в 10:30–11:30...")
        conflicts = schedule.check_room_conflict(
            room_id=room_2.id,
            lesson_date=test_date,
            time_start=time(10, 30),
            time_end=time(11, 30),
        )
        print(f"   Найдено конфликтов: {len(conflicts)}\n")

        print("4. Проверяем слот 09:00–10:00 (до занятия)...")
        conflicts = schedule.check_room_conflict(
            room_id=room_1.id,
            lesson_date=test_date,
            time_start=time(9, 0),
            time_end=time(10, 0),
        )
        print(f"   Найдено конфликтов: {len(conflicts)}")
        print("   (10:00 == 10:00 — не пересечение)\n")

        print("5. Проверяем слот 11:00–12:00 (сразу после)...")
        conflicts = schedule.check_room_conflict(
            room_id=room_1.id,
            lesson_date=test_date,
            time_start=time(11, 0),
            time_end=time(12, 0),
        )
        print(f"   Найдено конфликтов: {len(conflicts)}")
        print("   (11:00 == 11:00 — не пересечение)\n")

        print("6. Проверяем преподавателя (то же время, другой кабинет)...")
        conflicts = schedule.check_teacher_conflict(
            teacher_id=teacher.id,
            lesson_date=test_date,
            time_start=time(10, 30),
            time_end=time(11, 30),
        )
        print(f"   Найдено конфликтов: {len(conflicts)}\n")

        print("7. Проверяем слот полностью свободный...")
        ok, messages = schedule.is_slot_available(
            room_id=room_2.id,
            teacher_id=teacher.id,
            lesson_date=test_date,
            time_start=time(14, 0),
            time_end=time(15, 0),
        )
        print(f"   Свободно: {ok}")
        if messages:
            for m in messages:
                print(f"   - {m}")
        print()

        print("8. Проверяем слот с конфликтом кабинета...")
        ok, messages = schedule.is_slot_available(
            room_id=room_1.id,
            teacher_id=teacher.id,
            lesson_date=test_date,
            time_start=time(10, 30),
            time_end=time(11, 30),
        )
        print(f"   Свободно: {ok}")
        for m in messages:
            print(f"   - {m}")
        print()

        print("9. Проверяем слот, где конфликтуют И кабинет, И преподаватель...")
        lessons.add(
            teacher_id=teacher.id,
            room_id=room_1.id,
            lesson_date=test_date,
            time_start=time(14, 0),
            time_end=time(15, 0),
            cost=Decimal("1000.00"),
        )
        ok, messages = schedule.is_slot_available(
            room_id=room_1.id,
            teacher_id=teacher.id,
            lesson_date=test_date,
            time_start=time(14, 30),
            time_end=time(15, 30),
        )
        print(f"   Свободно: {ok}")
        for m in messages:
            print(f"   - {m}")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
