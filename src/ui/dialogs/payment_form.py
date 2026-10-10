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
            text="Пополнение баланса",
            style="Header.TLabel",
        ).pack(pady=(0, 25))

        ttk.Label(frame, text="Ученик:").pack(anchor="w", pady=(0, 6))
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(
            frame, textvariable=self.student_var, state="readonly"
        )
        self.student_combo.pack(fill="x", pady=(0, 15))
        self._load_students()

        ttk.Label(frame, text="Сумма пополнения, ₽:").pack(
            anchor="w", pady=(0, 6)
        )
        self.amount_var = tk.StringVar(value="1000.00")
        ttk.Entry(frame, textvariable=self.amount_var).pack(
            fill="x", pady=(0, 15)
        )

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(20, 0))
        btn_inner = ttk.Frame(btn_frame)
        btn_inner.pack(anchor="center")

        ttk.Button(
            btn_inner, text="Пополнить", command=self._save, width=15
        ).pack(side="left", padx=8)
        ttk.Button(
            btn_inner, text="Отмена", command=self.destroy, width=15
        ).pack(side="left", padx=8)

    def _load_students(self) -> None:
        """Загружает список учеников в комбобокс."""
        repo = StudentRepository(self.session)
        students = repo.list_all()
        self._student_map = {
            f"{s.id}: {s.full_name}": s.id for s in students
        }
        self.student_combo["values"] = list(self._student_map.keys())
        if students:
            self.student_var.set(list(self._student_map.keys())[0])

    def _save(self) -> None:
        """Пополняет баланс через FinanceService."""
        if not self.student_var.get():
            messagebox.showwarning(
                "Ошибка", "Выберите ученика", parent=self
            )
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
        px = parent.winfo_rootx() + (
            parent.winfo_width() - self.winfo_width()
        ) // 2
        py = parent.winfo_rooty() + (
            parent.winfo_height() - self.winfo_height()
        ) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")
