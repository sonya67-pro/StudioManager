"""Модальная форма для добавления/редактирования ученика."""
import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Student
from src.repositories.student_repo import StudentRepository
from src.ui import theme


class StudentForm(tk.Toplevel):
    """Диалог для создания или редактирования ученика.

    Attributes:
        session: Сессия SQLAlchemy.
        student: Редактируемый ученик (None — создание нового).
        result: Созданный/обновлённый ученик после закрытия.
    """

    def __init__(
        self,
        parent: tk.Widget,
        session: Session,
        student: Student | None = None,
    ) -> None:
        """Инициализирует форму.

        Args:
            parent: Родительское окно.
            session: Сессия SQLAlchemy.
            student: Ученик для редактирования (None — создание).
        """
        super().__init__(parent)
        self.session = session
        self.student = student
        self.result: Student | None = None

        self.title("Редактирование ученика" if student else "Новый ученик")
        self.geometry("500x480")
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
            text="Редактирование ученика" if self.student else "Новый ученик",
            style="Header.TLabel",
        ).pack(pady=(0, 25))

        ttk.Label(frame, text="ФИО:").pack(anchor="w", pady=(0, 6))
        self.name_var = tk.StringVar(
            value=self.student.full_name if self.student else ""
        )
        ttk.Entry(frame, textvariable=self.name_var).pack(fill="x", pady=(0, 15))

        ttk.Label(frame, text="Телефон:").pack(anchor="w", pady=(0, 6))
        self.phone_var = tk.StringVar(
            value=(self.student.phone or "") if self.student else ""
        )
        ttk.Entry(frame, textvariable=self.phone_var).pack(fill="x", pady=(0, 15))

        if self.student:
            ttk.Label(frame, text="Баланс:").pack(anchor="w", pady=(0, 6))
            ttk.Label(
                frame,
                text=f"{self.student.balance} ₽",
                font=(theme.FONT, 14, "bold"),
                foreground=theme.COLORS["primary_hover"],
            ).pack(anchor="w", pady=(0, 20))

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
        """Сохраняет ученика в БД."""
        full_name = self.name_var.get().strip()
        phone = self.phone_var.get().strip() or None

        if not full_name:
            messagebox.showwarning(
                "Ошибка", "ФИО не может быть пустым", parent=self
            )
            return

        try:
            repo = StudentRepository(self.session)
            if self.student:
                self.student.full_name = full_name
                self.student.phone = phone
                self.session.commit()
                self.session.refresh(self.student)
                self.result = self.student
            else:
                self.result = repo.add(full_name=full_name, phone=phone)
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
