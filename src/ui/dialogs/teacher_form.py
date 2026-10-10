"""Модальная форма для добавления/редактирования преподавателя."""
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Teacher
from src.repositories.teacher_repo import TeacherRepository


class TeacherForm(tk.Toplevel):
    """Диалог для создания или редактирования преподавателя.

    Attributes:
        session: Сессия SQLAlchemy.
        teacher: Редактируемый преподаватель (None — создание).
        result: Созданный/обновлённый преподаватель после закрытия.
    """

    def __init__(
        self,
        parent: tk.Widget,
        session: Session,
        teacher: Teacher | None = None,
    ) -> None:
        """Инициализирует форму.

        Args:
            parent: Родительское окно.
            session: Сессия SQLAlchemy.
            teacher: Преподаватель для редактирования (None — создание).
        """
        super().__init__(parent)
        self.session = session
        self.teacher = teacher
        self.result: Teacher | None = None

        self.title(
            "Редактирование преподавателя"
            if teacher
            else "Новый преподаватель"
        )
        self.geometry("500x540")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center(parent)

    def _build_ui(self) -> None:
        """Создаёт поля формы."""
        frame = ttk.Frame(self, padding=30)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=(
                "Редактирование преподавателя"
                if self.teacher
                else "Новый преподаватель"
            ),
            style="Header.TLabel",
        ).pack(pady=(0, 25))

        ttk.Label(frame, text="ФИО:").pack(anchor="w", pady=(0, 6))
        self.name_var = tk.StringVar(
            value=self.teacher.full_name if self.teacher else ""
        )
        ttk.Entry(frame, textvariable=self.name_var).pack(
            fill="x", pady=(0, 15)
        )

        ttk.Label(frame, text="Ставка за занятие, ₽:").pack(
            anchor="w", pady=(0, 6)
        )
        self.rate_var = tk.StringVar(
            value=str(self.teacher.rate) if self.teacher else "1000.00"
        )
        ttk.Entry(frame, textvariable=self.rate_var).pack(
            fill="x", pady=(0, 15)
        )

        ttk.Label(frame, text="Комиссия, %:").pack(anchor="w", pady=(0, 6))
        self.commission_var = tk.StringVar(
            value=(
                str(self.teacher.commission_percent)
                if self.teacher
                else "30.00"
            )
        )
        ttk.Entry(frame, textvariable=self.commission_var).pack(
            fill="x", pady=(0, 15)
        )

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(20, 0))
        btn_inner = ttk.Frame(btn_frame)
        btn_inner.pack(anchor="center")

        ttk.Button(
            btn_inner, text="Сохранить", command=self._save, width=15
        ).pack(side="left", padx=8)
        ttk.Button(
            btn_inner, text="Отмена", command=self.destroy, width=15
        ).pack(side="left", padx=8)

    def _save(self) -> None:
        """Сохраняет преподавателя в БД."""
        full_name = self.name_var.get().strip()
        if not full_name:
            messagebox.showwarning(
                "Ошибка", "ФИО не может быть пустым", parent=self
            )
            return

        try:
            rate = Decimal(self.rate_var.get().strip())
            commission = Decimal(self.commission_var.get().strip())
        except (InvalidOperation, ValueError):
            messagebox.showwarning(
                "Ошибка",
                "Ставка и комиссия должны быть числами",
                parent=self,
            )
            return

        if rate <= 0:
            messagebox.showwarning(
                "Ошибка", "Ставка должна быть положительной", parent=self
            )
            return

        if not (Decimal("0") <= commission <= Decimal("100")):
            messagebox.showwarning(
                "Ошибка",
                "Комиссия должна быть в диапазоне 0–100%",
                parent=self,
            )
            return

        try:
            repo = TeacherRepository(self.session)
            if self.teacher:
                self.teacher.full_name = full_name
                self.teacher.rate = rate
                self.teacher.commission_percent = commission
                self.session.commit()
                self.session.refresh(self.teacher)
                self.result = self.teacher
            else:
                self.result = repo.add(
                    full_name=full_name,
                    rate=rate,
                    commission_percent=commission,
                )
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Ошибка", str(e), parent=self)
            return

        self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        """Центрирует диалог относительно родителя."""
        self.update_idletasks()
        px = parent.winfo_rootx() + (
            parent.winfo_width() - self.winfo_width()
        ) // 2
        py = parent.winfo_rooty() + (
            parent.winfo_height() - self.winfo_height()
        ) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")
