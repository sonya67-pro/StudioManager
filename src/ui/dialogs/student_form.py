"""Модальная форма для добавления/редактирования ученика."""
import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Student
from src.repositories.student_repo import StudentRepository


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
        self.geometry("420x280")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center(parent)

    def _build_ui(self) -> None:
        """Создаёт поля формы."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="ФИО:").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.name_var = tk.StringVar(
            value=self.student.full_name if self.student else ""
        )
        ttk.Entry(frame, textvariable=self.name_var, width=40).grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        ttk.Label(frame, text="Телефон:").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.phone_var = tk.StringVar(
            value=(self.student.phone or "") if self.student else ""
        )
        ttk.Entry(frame, textvariable=self.phone_var, width=40).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        if self.student:
            ttk.Label(frame, text="Баланс:").grid(
                row=4, column=0, sticky="w", pady=(0, 5)
            )
            ttk.Label(
                frame,
                text=f"{self.student.balance} ₽",
                font=("Segoe UI", 10, "bold"),
            ).grid(row=5, column=0, sticky="w", pady=(0, 15))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="e")

        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(
            side="right", padx=(10, 0)
        )
        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(
            side="right"
        )

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
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")
