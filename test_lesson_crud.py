"""Проверка CRUD-операций через LessonRepository."""
from datetime import date, time
from decimal import Decimal

from src.db.database import get_session, init_db
from src.repositories.lesson_repo import LessonRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.teacher_repo import TeacherRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория занятий."""
    init_db()
    print("=== Проверка CRUD занятий ===\n")

    with get_session() as session:
        students = StudentRepository(session)
        teachers = TeacherRepository(session)
        rooms = RoomRepository(session)
        lessons = LessonRepository(session)

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
        print(f"   Преподаватель: {teacher.full_name}")
        print(f"   Кабинет: {room.name}\n")

        print("1. Создаём индивидуальное занятие...")
        lesson_ind = lessons.add(
            teacher_id=teacher.id,
            room_id=room.id,
            lesson_date=date(2026, 10, 15),
            time_start=time(10, 0),
            time_end=time(11, 0),
            cost=Decimal("1000.00"),
            is_group=False,
        )
        print(f"   Создано: id={lesson_ind.id}, "
              f"дата={lesson_ind.date}, статус={lesson_ind.status}\n")

        print("2. Создаём групповое занятие...")
        lesson_group = lessons.add(
            teacher_id=teacher.id,
            room_id=room.id,
            lesson_date=date(2026, 10, 15),
            time_start=time(12, 0),
            time_end=time(13, 30),
            cost=Decimal("800.00"),
            is_group=True,
        )
        print(f"   Создано: id={lesson_group.id}, "
              f"дата={lesson_group.date}, статус={lesson_group.status}\n")

        print("3. Добавляем учеников к групповому занятию...")
        lessons.add_student(lesson_group.id, ivanov.id)
        lessons.add_student(lesson_group.id, petrov.id)
        lesson_group = lessons.get(lesson_group.id)
        print(f"   Учеников в группе: {len(lesson_group.students)}")
        for student in lesson_group.students:
            print(f"     - {student.full_name}")
        print()

        print("4. Занятия на 15.10.2026:")
        for lesson in lessons.list_by_date(date(2026, 10, 15)):
            group_label = "групповое" if lesson.is_group else "индивидуальное"
            print(f"   [{lesson.id}] {lesson.time_start}-{lesson.time_end} — "
                  f"{group_label}, статус: {lesson.status}")
        print()

        print("5. Занятия преподавателя Ивановой:")
        for lesson in lessons.list_by_teacher(teacher.id):
            print(f"   [{lesson.id}] {lesson.date} {lesson.time_start}")
        print()

        print("6. Отмечаем индивидуальное как проведённое...")
        lesson_ind = lessons.mark_done(lesson_ind.id)
        print(f"   Статус: {lesson_ind.status}\n")

        print("7. Отмечаем индивидуальное как оплаченное...")
        lesson_ind = lessons.mark_paid(lesson_ind.id)
        print(f"   Статус: {lesson_ind.status}\n")

        print("8. Отменяем групповое занятие...")
        lesson_group = lessons.cancel(lesson_group.id)
        print(f"   Статус: {lesson_group.status}\n")

        print("9. Удаляем индивидуальное занятие...")
        deleted = lessons.delete(lesson_ind.id)
        print(f"   Удалено: {deleted}\n")

        print("10. Итоговый список:")
        for lesson in lessons.list_all():
            print(f"   [{lesson.id}] {lesson.date} {lesson.time_start} — "
                  f"статус: {lesson.status}")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
