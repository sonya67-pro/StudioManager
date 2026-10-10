"""Экран «Финансы»: платежи учеников, балансы и должники."""
import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.repositories.payment_repo import PaymentRepository
from src.repositories.student_repo import StudentRepository
from src.services.finance_service import FinanceService
from src.ui import theme
from src.ui.dialogs.payment_form import PaymentForm
from src.ui.widgets import RoundedButton


class FinanceView(ttk.Frame):
    """Экран управления финансами."""

    def __init__(self, parent: tk.Widget, session: Session) -> None:
        """Инициализирует экран.

        Args:
            parent: Родительский виджет.
            session: Сессия SQLAlchemy.
        """
        super().__init__(parent)
        self.session = session
        self.payments = PaymentRepository(session)
        self.students = StudentRepository(session)
        self.finance = FinanceService(session)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Создаёт панель кнопок и таблицу платежей."""
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        RoundedButton(
            top, text="Пополнить баланс", command=self._on_top_up,
            width=180, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Должники", command=self._show_debtors,
            bg_color=theme.COLORS["warning"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["warning_border"],
            hover_color=theme.COLORS["warning_border"],
            width=140, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Обновить", command=self.refresh,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        columns = ("id", "date", "student", "amount")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", selectmode="browse"
        )

        headers = [
            ("id", "ID", 60, "center"),
            ("date", "Дата", 120, "center"),
            ("student", "Ученик", 400, "w"),
            ("amount", "Сумма, ₽", 150, "e"),
        ]
        for col, text, width, anchor in headers:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self) -> None:
        """Обновляет таблицу платежей."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        student_map = {s.id: s.full_name for s in self.students.list_all()}

        for payment in self.payments.list_all():
            student_name = student_map.get(payment.student_id, "—")
            self.tree.insert(
                "",
                "end",
                iid=str(payment.id),
                values=(
                    payment.id,
                    payment.date.isoformat(),
                    student_name,
                    f"{payment.amount:.2f}",
                ),
            )

    def _on_top_up(self) -> None:
        """Открывает форму пополнения баланса."""
        form = PaymentForm(self, self.session)
        self.wait_window(form)
        if form.result:
            self.refresh()

    def _show_debtors(self) -> None:
        """Показывает список должников."""
        debtors = self.finance.get_debtors()
        if not debtors:
            messagebox.showinfo("Должники", "Должников нет", parent=self)
            return

        text = "Список должников:\n\n"
        for sid, name, balance in debtors:
            text += f"• {name} — баланс {balance} ₽\n"

        messagebox.showinfo("Должники", text, parent=self)
