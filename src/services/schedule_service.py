"""Сервис проверки расписания: конфликты кабинетов и преподавателей."""
from datetime import date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Lesson
from src.repositories.lesson_repo import LessonRepository


class ScheduleService:
    """Проверка конфликтов расписания.

    Attributes:
        session: Активная сессия SQLAlchemy.
        lessons: Репозиторий занятий.
    """

    def __init__(self, session: Session) -> None:
        """Инициализирует сервис с заданной сессией.

        Args:
            session: Сессия SQLAlchemy для работы с БД.
        """
        self.session = session
        self.lessons = LessonRepository(session)

    @staticmethod
    def _overlaps(
        a_start: time,
        a_end: time,
        b_start: time,
        b_end: time,
    ) -> bool:
        """Проверяет, пересекаются ли два временных интервала.

        Args:
            a_start: Начало первого интервала.
            a_end: Конец первого интервала.
            b_start: Начало второго интервала.
            b_end: Конец второго интервала.

        Returns:
            True, если интервалы пересекаются.
        """
        return a_start < b_end and b_start < a_end

    def check_room_conflict(
        self,
        room_id: int,
        lesson_date: date,
        time_start: time,
        time_end: time,
        exclude_lesson_id: int | None = None,
    ) -> list[Lesson]:
        """Находит занятия, конфликтующие по кабинету (FR-13).

        Args:
            room_id: ID кабинета.
            lesson_date: Дата занятия.
            time_start: Время начала.
            time_end: Время окончания.
            exclude_lesson_id: ID занятия, которое надо игнорировать.

        Returns:
            Список конфликтующих занятий.
        """
        statement = select(Lesson).where(
            Lesson.room_id == room_id,
            Lesson.date == lesson_date,
            Lesson.status != "cancelled",
        )
        existing = list(self.session.scalars(statement).all())

        conflicts: list[Lesson] = []
        for lesson in existing:
            if exclude_lesson_id is not None and lesson.id == exclude_lesson_id:
                continue
            if self._overlaps(
                time_start, time_end, lesson.time_start, lesson.time_end
            ):
                conflicts.append(lesson)
        return conflicts

    def check_teacher_conflict(
        self,
        teacher_id: int,
        lesson_date: date,
        time_start: time,
        time_end: time,
        exclude_lesson_id: int | None = None,
    ) -> list[Lesson]:
        """Находит занятия, конфликтующие у преподавателя.

        Args:
            teacher_id: ID преподавателя.
            lesson_date: Дата занятия.
            time_start: Время начала.
            time_end: Время окончания.
            exclude_lesson_id: ID занятия, которое надо игнорировать.

        Returns:
            Список конфликтующих занятий.
        """
        statement = select(Lesson).where(
            Lesson.teacher_id == teacher_id,
            Lesson.date == lesson_date,
            Lesson.status != "cancelled",
        )
        existing = list(self.session.scalars(statement).all())

        conflicts: list[Lesson] = []
        for lesson in existing:
            if exclude_lesson_id is not None and lesson.id == exclude_lesson_id:
                continue
            if self._overlaps(
                time_start, time_end, lesson.time_start, lesson.time_end
            ):
                conflicts.append(lesson)
        return conflicts

    def is_slot_available(
        self,
        room_id: int,
        teacher_id: int,
        lesson_date: date,
        time_start: time,
        time_end: time,
        exclude_lesson_id: int | None = None,
    ) -> tuple[bool, list[str]]:
        """Проверяет, свободен ли слот для занятия.

        Args:
            room_id: ID кабинета.
            teacher_id: ID преподавателя.
            lesson_date: Дата.
            time_start: Время начала.
            time_end: Время окончания.
            exclude_lesson_id: ID занятия, которое надо игнорировать.

        Returns:
            Кортеж (свободно ли, список сообщений о конфликтах).
        """
        messages: list[str] = []

        room_conflicts = self.check_room_conflict(
            room_id, lesson_date, time_start, time_end, exclude_lesson_id
        )
        if room_conflicts:
            ids = ", ".join(str(lesson.id) for lesson in room_conflicts)
            messages.append(
                f"Кабинет занят (конфликт с занятиями: {ids})"
            )

        teacher_conflicts = self.check_teacher_conflict(
            teacher_id, lesson_date, time_start, time_end, exclude_lesson_id
        )
        if teacher_conflicts:
            ids = ", ".join(str(lesson.id) for lesson in teacher_conflicts)
            messages.append(
                f"Преподаватель занят (конфликт с занятиями: {ids})"
            )

        return (len(messages) == 0, messages)
