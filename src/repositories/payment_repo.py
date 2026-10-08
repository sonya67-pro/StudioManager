"""Репозиторий для работы с платежами учеников (таблица payments)."""
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Payment


class PaymentRepository:
    """CRUD-операции над платежами учеников.

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
        student_id: int,
        amount: Decimal,
        payment_date: date | None = None,
    ) -> Payment:
        """Создаёт новый платёж.

        Args:
            student_id: ID ученика.
            amount: Сумма платежа (положительная).
            payment_date: Дата платежа (по умолчанию — сегодня).

        Returns:
            Созданный объект Payment.

        Raises:
            ValueError: Если сумма не положительная.
        """
        if amount <= 0:
            raise ValueError("Сумма платежа должна быть положительной")

        payment = Payment(
            student_id=student_id,
            amount=amount,
            date=payment_date or date.today(),
        )
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def get(self, payment_id: int) -> Payment | None:
        """Возвращает платёж по id или None, если не найден.

        Args:
            payment_id: Первичный ключ платежа.

        Returns:
            Объект Payment или None.
        """
        return self.session.get(Payment, payment_id)

    def list_all(self) -> list[Payment]:
        """Возвращает список всех платежей, отсортированный по дате.

        Returns:
            Список объектов Payment.
        """
        statement = select(Payment).order_by(Payment.date, Payment.id)
        return list(self.session.scalars(statement).all())

    def list_by_student(self, student_id: int) -> list[Payment]:
        """Возвращает платежи конкретного ученика.

        Args:
            student_id: ID ученика.

        Returns:
            Список платежей ученика.
        """
        statement = (
            select(Payment)
            .where(Payment.student_id == student_id)
            .order_by(Payment.date, Payment.id)
        )
        return list(self.session.scalars(statement).all())

    def delete(self, payment_id: int) -> bool:
        """Удаляет платёж по id.

        Args:
            payment_id: ID платежа.

        Returns:
            True, если платёж был удалён, иначе False.
        """
        payment = self.get(payment_id)
        if payment is None:
            return False
        self.session.delete(payment)
        self.session.commit()
        return True
