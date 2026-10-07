"""ORM-модели базы данных StudioManager.

Модели описывают таблицы SQLite согласно ER-диаграмме из ТЗ:
ученики, преподаватели, кабинеты, занятия, платежи, выплаты.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


# Ассоциативная таблица для связи «многие-ко-многим»:
# одно занятие — много учеников (групповое),
# один ученик — много занятий.
lesson_students = Table(
    "lesson_students",
    Base.metadata,
    Column(
        "lesson_id",
        ForeignKey("lessons.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "student_id",
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Student(Base):
    """Ученик студии.

    Attributes:
        id: Первичный ключ.
        full_name: ФИО ученика.
        phone: Телефон (опционально).
        balance: Текущий баланс в рублях (не может быть отрицательным).
    """

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="student", cascade="all, delete-orphan"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", secondary=lesson_students, back_populates="students"
    )

    __table_args__ = (
        CheckConstraint("balance >= 0", name="ck_students_balance_non_negative"),
    )

    def __repr__(self) -> str:
        """Строковое представление ученика."""
        return f"<Student id={self.id} name={self.full_name!r} balance={self.balance}>"


class Teacher(Base):
    """Преподаватель студии.

    Attributes:
        id: Первичный ключ.
        full_name: ФИО преподавателя.
        rate: Ставка за одно занятие, руб.
        commission_percent: Процент комиссии преподавателя (0–100).
    """

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    commission_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00")
    )

    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="teacher")
    payouts: Mapped[list["Payout"]] = relationship(
        "Payout", back_populates="teacher", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "commission_percent >= 0 AND commission_percent <= 100",
            name="ck_teachers_commission_range",
        ),
    )

    def __repr__(self) -> str:
        """Строковое представление преподавателя."""
        return f"<Teacher id={self.id} name={self.full_name!r} rate={self.rate}>"


class Room(Base):
    """Кабинет для занятий.

    Attributes:
        id: Первичный ключ.
        name: Название/номер кабинета (уникально).
        capacity: Вместимость (сколько человек помещается).
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        """Строковое представление кабинета."""
        return f"<Room id={self.id} name={self.name!r}>"


class Lesson(Base):
    """Занятие (индивидуальное или групповое).

    Статусы: ``planned``, ``done``, ``cancelled``, ``paid``.

    Attributes:
        id: Первичный ключ.
        teacher_id: FK на преподавателя.
        room_id: FK на кабинет.
        date: Дата занятия.
        time_start: Время начала.
        time_end: Время окончания.
        is_group: 1 — групповое, 0 — индивидуальное.
        status: Статус занятия.
        cost: Стоимость занятия, руб.
    """

    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="RESTRICT"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    time_start: Mapped[str] = mapped_column(Time, nullable=False)
    time_end: Mapped[str] = mapped_column(Time, nullable=False)
    is_group: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="lessons")
    room: Mapped["Room"] = relationship("Room")
    students: Mapped[list["Student"]] = relationship(
        "Student", secondary=lesson_students, back_populates="lessons"
    )

    __table_args__ = (
        Index("idx_lessons_date", "date"),
        Index("idx_lessons_teacher", "teacher_id"),
        CheckConstraint(
            "status IN ('planned', 'done', 'cancelled', 'paid')",
            name="ck_lessons_status_valid",
        ),
    )

    def __repr__(self) -> str:
        """Строковое представление занятия."""
        return f"<Lesson id={self.id} date={self.date} status={self.status!r}>"


class Payment(Base):
    """Платёж ученика (пополнение баланса).

    Attributes:
        id: Первичный ключ.
        student_id: FK на ученика.
        amount: Сумма платежа (положительная).
        date: Дата платежа.
    """

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    student: Mapped["Student"] = relationship("Student", back_populates="payments")

    __table_args__ = (
        Index("idx_payments_student", "student_id"),
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
    )

    def __repr__(self) -> str:
        """Строковое представление платежа."""
        return (
            f"<Payment id={self.id} student_id={self.student_id} amount={self.amount}>"
        )


class Payout(Base):
    """Выплата комиссионных преподавателю.

    Attributes:
        id: Первичный ключ.
        teacher_id: FK на преподавателя.
        amount: Сумма выплаты.
        period_start: Начало периода.
        period_end: Конец периода.
        is_paid: 1 — выплачено, 0 — нет.
    """

    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    is_paid: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="payouts")

    def __repr__(self) -> str:
        """Строковое представление выплаты."""
        return (
            f"<Payout id={self.id} teacher_id={self.teacher_id} amount={self.amount}>"
        )
