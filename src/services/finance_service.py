"""Сервис финансовых операций: баланс, платежи, комиссии, выплаты."""
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from src.repositories.payment_repo import PaymentRepository
from src.repositories.payout_repo import PayoutRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.teacher_repo import TeacherRepository


class FinanceService:
    """Бизнес-логика финансовых операций студии.

    Attributes:
        session: Активная сессия SQLAlchemy.
        students: Репозиторий учеников.
        teachers: Репозиторий преподавателей.
        payments: Репозиторий платежей.
        payouts: Репозиторий выплат.
    """

    def __init__(self, session: Session) -> None:
        """Инициализирует сервис с заданной сессией.

        Args:
            session: Сессия SQLAlchemy для работы с БД.
        """
        self.session = session
        self.students = StudentRepository(session)
        self.teachers = TeacherRepository(session)
        self.payments = PaymentRepository(session)
        self.payouts = PayoutRepository(session)

    def top_up_balance(
        self,
        student_id: int,
        amount: Decimal,
        payment_date: date | None = None,
    ) -> Decimal:
        """Пополняет баланс ученика и создаёт запись о платеже (FR-03).

        Операция атомарна: либо и платёж, и баланс обновятся,
        либо ничего не произойдёт.

        Args:
            student_id: ID ученика.
            amount: Сумма пополнения (положительная).
            payment_date: Дата платежа (по умолчанию — сегодня).

        Returns:
            Новый баланс ученика.

        Raises:
            ValueError: Если сумма не положительная или ученик не найден.
        """
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")

        student = self.students.get(student_id)
        if student is None:
            raise ValueError(f"Ученик с id={student_id} не найден")

        try:
            self.payments.add(
                student_id=student_id,
                amount=amount,
                payment_date=payment_date,
            )
            student = self.students.update_balance(student_id, amount)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return student.balance

    def charge_lesson(self, student_id: int, cost: Decimal) -> Decimal:
        """Списывает стоимость занятия с баланса ученика (FR-04).

        Args:
            student_id: ID ученика.
            cost: Стоимость занятия (положительная).

        Returns:
            Новый баланс ученика.

        Raises:
            ValueError: Если стоимость не положительная,
                ученик не найден или недостаточно средств.
        """
        if cost <= 0:
            raise ValueError("Стоимость занятия должна быть положительной")

        try:
            student = self.students.update_balance(student_id, -cost)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return student.balance

    def get_debtors(self) -> list[tuple[int, str, Decimal]]:
        """Возвращает список учеников с нулевым балансом (FR-05).

        Returns:
            Список кортежей (id, ФИО, баланс).
        """
        debtors: list[tuple[int, str, Decimal]] = []
        for student in self.students.list_all():
            if student.balance <= 0:
                debtors.append((student.id, student.full_name, student.balance))
        return debtors

    def calc_teacher_commission(
        self,
        teacher_id: int,
        period_start: date,
        period_end: date,
    ) -> Decimal:
        """Считает комиссию преподавателя за период (FR-15).

        Формула: ставка × процент / 100 × количество занятий.
        Считаются только занятия со статусом 'done' или 'paid'.

        Args:
            teacher_id: ID преподавателя.
            period_start: Начало периода.
            period_end: Конец периода.

        Returns:
            Итоговая сумма комиссии.

        Raises:
            ValueError: Если преподаватель не найден или период некорректен.
        """
        if period_end < period_start:
            raise ValueError("Конец периода должен быть не раньше начала")

        teacher = self.teachers.get(teacher_id)
        if teacher is None:
            raise ValueError(f"Преподаватель с id={teacher_id} не найден")

        from src.repositories.lesson_repo import LessonRepository

        lessons = LessonRepository(self.session)
        teacher_lessons = lessons.list_by_teacher(teacher_id)

        total = Decimal("0.00")
        for lesson in teacher_lessons:
            if period_start <= lesson.date <= period_end:
                if lesson.status in ("done", "paid"):
                    total += lesson.cost

        commission = (total * teacher.commission_percent / Decimal("100")).quantize(
            Decimal("0.01")
        )
        return commission

    def create_payout(
        self,
        teacher_id: int,
        period_start: date,
        period_end: date,
    ) -> int:
        """Создаёт ведомость выплаты преподавателю (FR-16).

        Args:
            teacher_id: ID преподавателя.
            period_start: Начало периода.
            period_end: Конец периода.

        Returns:
            ID созданной выплаты.

        Raises:
            ValueError: Если комиссия равна нулю или преподаватель не найден.
        """
        amount = self.calc_teacher_commission(teacher_id, period_start, period_end)
        if amount <= 0:
            raise ValueError(
                "Комиссия за период равна нулю — нечего выплачивать"
            )

        try:
            payout = self.payouts.add(
                teacher_id=teacher_id,
                amount=amount,
                period_start=period_start,
                period_end=period_end,
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return payout.id
