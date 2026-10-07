"""Репозиторий для работы с учениками (таблица students)."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Student


class StudentRepository:
    """CRUD-операции над учениками.

    Attributes:
        session: Активная сессия SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """Инициализирует репозиторий с заданной сессией.

        Args:
            session: Сессия SQLAlchemy для работы с БД.
        """
        self.session = session

    def add(self, full_name: str, phone: str | None = None) -> Student:
        """Создаёт нового ученика.

        Args:
            full_name: ФИО ученика.
            phone: Телефон (опционально).

        Returns:
            Созданный объект Student с присвоенным id.
        """
        student = Student(full_name=full_name, phone=phone)
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def get(self, student_id: int) -> Student | None:
        """Возвращает ученика по id или None, если не найден.

        Args:
            student_id: Первичный ключ ученика.

        Returns:
            Объект Student или None.
        """
        return self.session.get(Student, student_id)

    def list_all(self) -> list[Student]:
        """Возвращает список всех учеников, отсортированный по id.

        Returns:
            Список объектов Student.
        """
        statement = select(Student).order_by(Student.id)
        return list(self.session.scalars(statement).all())

    def find_by_name(self, query: str) -> list[Student]:
        """Ищет учеников по подстроке в ФИО (регистронезависимо).

        SQLite не поддерживает регистронезависимый поиск для кириллицы
        на уровне SQL (функция ``lower()`` обрабатывает только ASCII).
        Поэтому фильтрация выполняется в Python — это корректно работает
        с любыми языками.

        Args:
            query: Строка поиска.

        Returns:
            Список подходящих учеников.
        """
        query_lower = query.lower()
        return [
            student
            for student in self.list_all()
            if query_lower in student.full_name.lower()
        ]

    def update_balance(self, student_id: int, delta: Decimal) -> Student:
        """Изменяет баланс ученика на delta.

        Args:
            student_id: ID ученика.
            delta: Сумма изменения (положительная — пополнение,
                отрицательная — списание).

        Returns:
            Обновлённый объект Student.

        Raises:
            ValueError: Если ученик не найден или баланс станет отрицательным.
        """
        student = self.get(student_id)
        if student is None:
            raise ValueError(f"Ученик с id={student_id} не найден")

        new_balance = student.balance + delta
        if new_balance < 0:
            raise ValueError(
                f"Недостаточно средств: баланс {student.balance}, списание {-delta}"
            )

        student.balance = new_balance
        self.session.commit()
        self.session.refresh(student)
        return student

    def delete(self, student_id: int) -> bool:
        """Удаляет ученика по id.

        Args:
            student_id: ID ученика.

        Returns:
            True, если ученик был удалён, иначе False.
        """
        student = self.get(student_id)
        if student is None:
            return False
        self.session.delete(student)
        self.session.commit()
        return True
