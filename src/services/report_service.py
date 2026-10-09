"""Сервис формирования отчётов и экспорта данных."""
import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from src.repositories.lesson_repo import LessonRepository
from src.repositories.payment_repo import PaymentRepository
from src.repositories.payout_repo import PayoutRepository
from src.repositories.student_repo import StudentRepository
from src.repositories.teacher_repo import TeacherRepository


class ReportService:
    """Формирование отчётов и экспорт в CSV/JSON.

    Attributes:
        session: Активная сессия SQLAlchemy.
        students: Репозиторий учеников.
        teachers: Репозиторий преподавателей.
        lessons: Репозиторий занятий.
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
        self.lessons = LessonRepository(session)
        self.payments = PaymentRepository(session)
        self.payouts = PayoutRepository(session)

    def get_income_summary(self) -> dict:
        """Возвращает общую сводку по финансам студии.

        Returns:
            Словарь с ключами:
            - students_count: количество учеников;
            - teachers_count: количество преподавателей;
            - lessons_count: количество занятий;
            - total_income: сумма всех платежей;
            - total_payouts: сумма всех выплат;
            - unpaid_payouts: сумма неоплаченных выплат.
        """
        payments = self.payments.list_all()
        payouts = self.payouts.list_all()
        unpaid = self.payouts.list_unpaid()

        total_income = sum((p.amount for p in payments), Decimal("0.00"))
        total_payouts = sum((p.amount for p in payouts), Decimal("0.00"))
        unpaid_payouts = sum((p.amount for p in unpaid), Decimal("0.00"))

        return {
            "students_count": len(self.students.list_all()),
            "teachers_count": len(self.teachers.list_all()),
            "lessons_count": len(self.lessons.list_all()),
            "total_income": total_income,
            "total_payouts": total_payouts,
            "unpaid_payouts": unpaid_payouts,
        }

    def export_students_csv(self, file_path: str | Path) -> int:
        """Экспортирует список учеников в CSV.

        Args:
            file_path: Путь к файлу.

        Returns:
            Количество записей в файле.
        """
        students = self.students.list_all()
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["ID", "ФИО", "Телефон", "Баланс"])
            for s in students:
                writer.writerow([s.id, s.full_name, s.phone or "", s.balance])
        return len(students)

    def export_lessons_csv(self, file_path: str | Path) -> int:
        """Экспортирует список занятий в CSV.

        Args:
            file_path: Путь к файлу.

        Returns:
            Количество записей в файле.
        """
        lessons = self.lessons.list_all()
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                ["ID", "Дата", "Начало", "Конец", "Преподаватель",
                 "Кабинет", "Тип", "Стоимость", "Статус"]
            )
            for lesson in lessons:
                teacher_name = (
                    lesson.teacher.full_name if lesson.teacher else "—"
                )
                room_name = lesson.room.name if lesson.room else "—"
                writer.writerow([
                    lesson.id,
                    lesson.date.isoformat(),
                    lesson.time_start.strftime("%H:%M"),
                    lesson.time_end.strftime("%H:%M"),
                    teacher_name,
                    room_name,
                    "Групповое" if lesson.is_group else "Индивидуальное",
                    lesson.cost,
                    lesson.status,
                ])
        return len(lessons)

    def export_full_json(self, file_path: str | Path) -> None:
        """Экспортирует все данные в JSON.

        Args:
            file_path: Путь к файлу.
        """
        data = {
            "exported_at": date.today().isoformat(),
            "students": [
                {
                    "id": s.id,
                    "full_name": s.full_name,
                    "phone": s.phone,
                    "balance": str(s.balance),
                }
                for s in self.students.list_all()
            ],
            "teachers": [
                {
                    "id": t.id,
                    "full_name": t.full_name,
                    "rate": str(t.rate),
                    "commission_percent": str(t.commission_percent),
                }
                for t in self.teachers.list_all()
            ],
            "lessons": [
                {
                    "id": lesson.id,
                    "date": lesson.date.isoformat(),
                    "time_start": lesson.time_start.strftime("%H:%M"),
                    "time_end": lesson.time_end.strftime("%H:%M"),
                    "teacher_id": lesson.teacher_id,
                    "room_id": lesson.room_id,
                    "is_group": bool(lesson.is_group),
                    "cost": str(lesson.cost),
                    "status": lesson.status,
                }
                for lesson in self.lessons.list_all()
            ],
            "payments": [
                {
                    "id": p.id,
                    "student_id": p.student_id,
                    "amount": str(p.amount),
                    "date": p.date.isoformat(),
                }
                for p in self.payments.list_all()
            ],
            "payouts": [
                {
                    "id": p.id,
                    "teacher_id": p.teacher_id,
                    "amount": str(p.amount),
                    "period_start": p.period_start.isoformat(),
                    "period_end": p.period_end.isoformat(),
                    "is_paid": bool(p.is_paid),
                }
                for p in self.payouts.list_all()
            ],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
