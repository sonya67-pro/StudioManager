"""Репозиторий для работы с преподавателями (таблица teachers)."""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Teacher


class TeacherRepository:
    """CRUD-операции над преподавателями.

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
        full_name: str,
        rate: Decimal,
        commission_percent: Decimal = Decimal("0.00"),
    ) -> Teacher:
        """Создаёт нового преподавателя.

        Args:
            full_name: ФИО преподавателя.
            rate: Ставка за одно занятие.
            commission_percent: Процент комиссии (0–100).

        Returns:
            Созданный объект Teacher с присвоенным id.
        """
        teacher = Teacher(
            full_name=full_name,
            rate=rate,
            commission_percent=commission_percent,
        )
        self.session.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def get(self, teacher_id: int) -> Teacher | None:
        """Возвращает преподавателя по id или None, если не найден.

        Args:
            teacher_id: Первичный ключ преподавателя.

        Returns:
            Объект Teacher или None.
        """
        return self.session.get(Teacher, teacher_id)

    def list_all(self) -> list[Teacher]:
        """Возвращает список всех преподавателей, отсортированный по id.

        Returns:
            Список объектов Teacher.
        """
        statement = select(Teacher).order_by(Teacher.id)
        return list(self.session.scalars(statement).all())

    def find_by_name(self, query: str) -> list[Teacher]:
        """Ищет преподавателей по подстроке в ФИО (регистронезависимо).

        SQLite не поддерживает регистронезависимый поиск для кириллицы
        на уровне SQL, поэтому фильтрация выполняется в Python.

        Args:
            query: Строка поиска.

        Returns:
            Список подходящих преподавателей.
        """
        query_lower = query.lower()
        return [
            teacher
            for teacher in self.list_all()
            if query_lower in teacher.full_name.lower()
        ]

    def update_rate(
        self,
        teacher_id: int,
        rate: Decimal,
        commission_percent: Decimal,
    ) -> Teacher:
        """Обновляет ставку и процент комиссии преподавателя.

        Args:
            teacher_id: ID преподавателя.
            rate: Новая ставка.
            commission_percent: Новый процент комиссии (0–100).

        Returns:
            Обновлённый объект Teacher.

        Raises:
            ValueError: Если преподаватель не найден или процент вне 0–100.
        """
        if not (Decimal("0") <= commission_percent <= Decimal("100")):
            raise ValueError("Процент комиссии должен быть в диапазоне 0–100")

        teacher = self.get(teacher_id)
        if teacher is None:
            raise ValueError(f"Преподаватель с id={teacher_id} не найден")

        teacher.rate = rate
        teacher.commission_percent = commission_percent
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def delete(self, teacher_id: int) -> bool:
        """Удаляет преподавателя по id.

        Args:
            teacher_id: ID преподавателя.

        Returns:
            True, если преподаватель был удалён, иначе False.
        """
        teacher = self.get(teacher_id)
        if teacher is None:
            return False
        self.session.delete(teacher)
        self.session.commit()
        return True
