"""Модальная форма пополнения баланса ученика."""
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.repositories.student_repo import StudentRepository
from src.services.finance_service import FinanceService


class PaymentForm(tk.Toplevel):
    """Диалог пополнения баланса ученика.

    Attributes:
        session: Сессия SQLAlchemy.
        result: True, если платёж добавлен.
    """

    def __init__(self, parent: tk.Widget, session: Session) -> None:
        """Инициализирует форму.

        Args:
            parent: Родительское окно.
            session: Сессия SQLAlchemy.
        """
        super().__init__(parent)
        self.session = session
        self.result = False

        self.title("Пополнение баланса")
        self.geometry("420x260")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center(parent)

    def _build_ui(self) -> None:
        """Создаёт поля формы."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Ученик
        ttk.Label(frame, text="Ученик:").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(
            frame, textvariable=self.student_var, state="readonly", width=37
        )
        self.student_combo.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )
        self._load_students()

        # Сумма
        ttk.Label(frame, text="Сумма пополнения, ₽:").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.amount_var = tk.StringVar(value="1000.00")
        ttk.Entry(frame, textvariable=self.amount_var, width=40).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0), sticky="e")

        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(
            side="right", padx=(10, 0)
        )
        ttk.Button(btn_frame, text="Пополнить", command=self._save).pack(
            side="right"
        )

    def _load_students(self) -> None:
        """Загружает список учеников в комбобокс."""
        repo = StudentRepository(self.session)
        students = repo.list_all()
        self._student_map = {f"{s.id}: {s.full_name}": s.id for s in students}
        self.student_combo["values"] = list(self._student_map.keys())
        if students:
            self.student_var.set(list(self._student_map.keys())[0])

    def _save(self) -> None:
        """Пополняет баланс через FinanceService."""
        if not self.student_var.get():
            messagebox.showwarning("Ошибка", "Выберите ученика", parent=self)
            return

        try:
            amount = Decimal(self.amount_var.get().strip())
        except (InvalidOperation, ValueError):
            messagebox.showwarning(
                "Ошибка", "Сумма должна быть числом", parent=self
            )
            return

        if amount <= 0:
            messagebox.showwarning(
                "Ошибка", "Сумма должна быть положительной", parent=self
            )
            return

        student_id = self._student_map[self.student_var.get()]

        try:
            service = FinanceService(self.session)
            service.top_up_balance(student_id, amount)
            self.result = True
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
