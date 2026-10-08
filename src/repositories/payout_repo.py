"""Репозиторий для работы с выплатами преподавателям (таблица payouts)."""
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Payout


class PayoutRepository:
    """CRUD-операции над выплатами преподавателям.

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
        amount: Decimal,
        period_start: date,
        period_end: date,
    ) -> Payout:
        """Создаёт новую выплату (ведомость) преподавателю.

        Args:
            teacher_id: ID преподавателя.
            amount: Сумма выплаты.
            period_start: Начало периода.
            period_end: Конец периода.

        Returns:
            Созданный объект Payout.

        Raises:
            ValueError: Если сумма не положительная или период некорректен.
        """
        if amount <= 0:
            raise ValueError("Сумма выплаты должна быть положительной")
        if period_end < period_start:
            raise ValueError("Конец периода должен быть не раньше начала")

        payout = Payout(
            teacher_id=teacher_id,
            amount=amount,
            period_start=period_start,
            period_end=period_end,
            is_paid=0,
        )
        self.session.add(payout)
        self.session.commit()
        self.session.refresh(payout)
        return payout

    def get(self, payout_id: int) -> Payout | None:
        """Возвращает выплату по id или None, если не найдена.

        Args:
            payout_id: Первичный ключ выплаты.

        Returns:
            Объект Payout или None.
        """
        return self.session.get(Payout, payout_id)

    def list_all(self) -> list[Payout]:
        """Возвращает список всех выплат, отсортированный по дате периода.

        Returns:
            Список объектов Payout.
        """
        statement = select(Payout).order_by(
            Payout.period_start, Payout.id
        )
        return list(self.session.scalars(statement).all())

    def list_by_teacher(self, teacher_id: int) -> list[Payout]:
        """Возвращает выплаты конкретного преподавателя.

        Args:
            teacher_id: ID преподавателя.

        Returns:
            Список выплат преподавателя.
        """
        statement = (
            select(Payout)
            .where(Payout.teacher_id == teacher_id)
            .order_by(Payout.period_start, Payout.id)
        )
        return list(self.session.scalars(statement).all())

    def list_unpaid(self) -> list[Payout]:
        """Возвращает только неоплаченные выплаты.

        Returns:
            Список неоплаченных Payout.
        """
        statement = (
            select(Payout)
            .where(Payout.is_paid == 0)
            .order_by(Payout.period_start, Payout.id)
        )
        return list(self.session.scalars(statement).all())

    def mark_paid(self, payout_id: int) -> Payout:
        """Отмечает выплату как произведённую.

        Args:
            payout_id: ID выплаты.

        Returns:
            Обновлённый объект Payout.

        Raises:
            ValueError: Если выплата не найдена.
        """
        payout = self.get(payout_id)
        if payout is None:
            raise ValueError(f"Выплата с id={payout_id} не найдена")
        payout.is_paid = 1
        self.session.commit()
        self.session.refresh(payout)
        return payout

    def delete(self, payout_id: int) -> bool:
        """Удаляет выплату по id.

        Args:
            payout_id: ID выплаты.

        Returns:
            True, если выплата была удалена, иначе False.
        """
        payout = self.get(payout_id)
        if payout is None:
            return False
        self.session.delete(payout)
        self.session.commit()
        return True
