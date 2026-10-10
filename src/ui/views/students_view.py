"""Экран «Ученики»: таблица и операции с учениками."""
import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Student
from src.repositories.student_repo import StudentRepository
from src.ui import theme
from src.ui.dialogs.student_form import StudentForm
from src.ui.widgets import RoundedButton


class StudentsView(ttk.Frame):
    """Экран управления учениками.

    Attributes:
        session: Сессия SQLAlchemy.
        repo: Репозиторий учеников.
        search_var: Строка поиска.
        tree: Таблица учеников.
    """

    def __init__(self, parent: tk.Widget, session: Session) -> None:
        """Инициализирует экран.

        Args:
            parent: Родительский виджет.
            session: Сессия SQLAlchemy.
        """
        super().__init__(parent)
        self.session = session
        self.repo = StudentRepository(session)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Создаёт панель поиска, таблицу и кнопки."""
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="Поиск:").pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ttk.Entry(top, textvariable=self.search_var, width=28).pack(
            side="left", padx=(0, 15)
        )

        RoundedButton(
            top,
            text="Добавить",
            command=self._on_add,
            width=130,
            height=38,
            radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top,
            text="Редактировать",
            command=self._on_edit,
            width=155,
            height=38,
            radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top,
            text="Удалить",
            command=self._on_delete,
            bg_color=theme.COLORS["danger"],
            border_color=theme.COLORS["danger_hover"],
            hover_color=theme.COLORS["danger_hover"],
            width=130,
            height=38,
            radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top,
            text="Обновить",
            command=self.refresh,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=130,
            height=38,
            radius=12,
        ).pack(side="left", padx=4)

        columns = ("id", "name", "phone", "balance")
        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ФИО")
        self.tree.heading("phone", text="Телефон")
        self.tree.heading("balance", text="Баланс, ₽")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("name", width=350, anchor="w")
        self.tree.column("phone", width=180, anchor="w")
        self.tree.column("balance", width=120, anchor="e")

        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda _: self._on_edit())

    def refresh(self) -> None:
        """Обновляет содержимое таблицы с учётом поиска."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self.search_var.get().strip()
        students = (
            self.repo.find_by_name(query) if query else self.repo.list_all()
        )

        for s in students:
            self.tree.insert(
                "",
                "end",
                iid=str(s.id),
                values=(
                    s.id,
                    s.full_name,
                    s.phone or "—",
                    f"{s.balance:.2f}",
                ),
            )

    def _get_selected(self) -> Student | None:
        """Возвращает выбранного ученика или None."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Информация",
                "Сначала выберите ученика в таблице",
                parent=self,
            )
            return None
        return self.repo.get(int(selection[0]))

    def _on_add(self) -> None:
        """Открывает форму создания ученика."""
        form = StudentForm(self, self.session)
        self.wait_window(form)
        if form.result is not None:
            self.refresh()

    def _on_edit(self) -> None:
        """Открывает форму редактирования выбранного ученика."""
        student = self._get_selected()
        if student is None:
            return
        form = StudentForm(self, self.session, student=student)
        self.wait_window(form)
        if form.result is not None:
            self.refresh()

    def _on_delete(self) -> None:
        """Удаляет выбранного ученика с подтверждением."""
        student = self._get_selected()
        if student is None:
            return

        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить ученика «{student.full_name}»?",
            parent=self,
        ):
            return

        try:
            self.repo.delete(student.id)
            self.refresh()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Ошибка", str(e), parent=self)
