"""Репозиторий для работы с занятиями (таблица lessons)."""
from datetime import date, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Lesson, Student


class LessonRepository:
    """CRUD-операции над занятиями.

    Attributes:
        session: Активная сессия SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """Инициализирует репозиторий с заданной сессией.

        Args:
            session: Сессия SQLAlchemy для работы с БД.
        """
        self.session = session

    def add(
        self,
        teacher_id: int,
        room_id: int,
        lesson_date: date,
        time_start: time,
        time_end: time,
        cost: Decimal,
        is_group: bool = False,
    ) -> Lesson:
        """Создаёт новое занятие.

        Args:
            teacher_id: ID преподавателя.
            room_id: ID кабинета.
            lesson_date: Дата занятия.
            time_start: Время начала.
            time_end: Время окончания.
            cost: Стоимость занятия.
            is_group: True — групповое, False — индивидуальное.

        Returns:
            Созданный объект Lesson.

        Raises:
            ValueError: Если время окончания не позже времени начала.
        """
        if time_end <= time_start:
            raise ValueError("Время окончания должно быть позже времени начала")

        lesson = Lesson(
            teacher_id=teacher_id,
            room_id=room_id,
            date=lesson_date,
            time_start=time_start,
            time_end=time_end,
            cost=cost,
            is_group=1 if is_group else 0,
            status="planned",
        )
        self.session.add(lesson)
        self.session.commit()
        self.session.refresh(lesson)
        return lesson

    def get(self, lesson_id: int) -> Lesson | None:
        """Возвращает занятие по id или None, если не найдено.

        Args:
            lesson_id: Первичный ключ занятия.

        Returns:
            Объект Lesson или None.
        """
        return self.session.get(Lesson, lesson_id)

    def list_all(self) -> list[Lesson]:
        """Возвращает список всех занятий, отсортированный по дате.

        Returns:
            Список объектов Lesson.
        """
        statement = select(Lesson).order_by(Lesson.date, Lesson.time_start)
        return list(self.session.scalars(statement).all())

    def list_by_date(self, target_date: date) -> list[Lesson]:
        """Возвращает занятия на указанную дату.

        Args:
            target_date: Дата, за которую нужны занятия.

        Returns:
            Список занятий на эту дату.
        """
        statement = (
            select(Lesson)
            .where(Lesson.date == target_date)
            .order_by(Lesson.time_start)
        )
        return list(self.session.scalars(statement).all())

    def list_by_teacher(self, teacher_id: int) -> list[Lesson]:
        """Возвращает все занятия преподавателя.

        Args:
            teacher_id: ID преподавателя.

        Returns:
            Список занятий преподавателя.
        """
        statement = (
            select(Lesson)
            .where(Lesson.teacher_id == teacher_id)
            .order_by(Lesson.date, Lesson.time_start)
        )
        return list(self.session.scalars(statement).all())

    def mark_done(self, lesson_id: int) -> Lesson:
        """Отмечает занятие как проведённое.

        Args:
            lesson_id: ID занятия.

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие не найдено.
        """
        return self._set_status(lesson_id, "done")

    def cancel(self, lesson_id: int) -> Lesson:
        """Отменяет занятие.

        Args:
            lesson_id: ID занятия.

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие не найдено.
        """
        return self._set_status(lesson_id, "cancelled")

    def mark_paid(self, lesson_id: int) -> Lesson:
        """Отмечает занятие как оплаченное.

        Args:
            lesson_id: ID занятия.

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие не найдено.
        """
        return self._set_status(lesson_id, "paid")

    def _set_status(self, lesson_id: int, status: str) -> Lesson:
        """Внутренний метод: устанавливает статус занятию.

        Args:
            lesson_id: ID занятия.
            status: Новый статус (planned, done, cancelled, paid).

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие не найдено.
        """
        lesson = self.get(lesson_id)
        if lesson is None:
            raise ValueError(f"Занятие с id={lesson_id} не найдено")
        lesson.status = status
        self.session.commit()
        self.session.refresh(lesson)
        return lesson

    def add_student(self, lesson_id: int, student_id: int) -> Lesson:
        """Добавляет ученика к занятию (для групповых).

        Args:
            lesson_id: ID занятия.
            student_id: ID ученика.

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие или ученик не найдены.
        """
        lesson = self.get(lesson_id)
        if lesson is None:
            raise ValueError(f"Занятие с id={lesson_id} не найдено")

        student = self.session.get(Student, student_id)
        if student is None:
            raise ValueError(f"Ученик с id={student_id} не найден")

        if student not in lesson.students:
            lesson.students.append(student)
            self.session.commit()
            self.session.refresh(lesson)
        return lesson

    def remove_student(self, lesson_id: int, student_id: int) -> Lesson:
        """Убирает ученика с занятия.

        Args:
            lesson_id: ID занятия.
            student_id: ID ученика.

        Returns:
            Обновлённый объект Lesson.

        Raises:
            ValueError: Если занятие не найдено.
        """
        lesson = self.get(lesson_id)
        if lesson is None:
            raise ValueError(f"Занятие с id={lesson_id} не найдено")

        student = self.session.get(Student, student_id)
        if student is not None and student in lesson.students:
            lesson.students.remove(student)
            self.session.commit()
            self.session.refresh(lesson)
        return lesson

    def delete(self, lesson_id: int) -> bool:
        """Удаляет занятие по id.

        Args:
            lesson_id: ID занятия.

        Returns:
            True, если занятие было удалено, иначе False.
        """
        lesson = self.get(lesson_id)
        if lesson is None:
            return False
        self.session.delete(lesson)
        self.session.commit()
        return True
