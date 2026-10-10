"""Экран «Занятия»: таблица и операции с занятиями."""
import tkinter as tk
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Lesson
from src.repositories.lesson_repo import LessonRepository
from src.ui import theme
from src.ui.dialogs.lesson_form import LessonForm
from src.ui.widgets import RoundedButton


class LessonsView(ttk.Frame):
    """Экран управления занятиями."""

    def __init__(self, parent: tk.Widget, session: Session) -> None:
        """Инициализирует экран.

        Args:
            parent: Родительский виджет.
            session: Сессия SQLAlchemy.
        """
        super().__init__(parent)
        self.session = session
        self.repo = LessonRepository(session)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Создаёт панель кнопок и таблицу."""
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        RoundedButton(
            top, text="Добавить", command=self._on_add,
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Редактировать", command=self._on_edit,
            width=155, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Провести", command=self._on_mark_done,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Отменить", command=self._on_cancel,
            bg_color=theme.COLORS["warning"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["warning_border"],
            hover_color=theme.COLORS["warning_border"],
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Удалить", command=self._on_delete,
            bg_color=theme.COLORS["danger"],
            border_color=theme.COLORS["danger_hover"],
            hover_color=theme.COLORS["danger_hover"],
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            top, text="Обновить", command=self.refresh,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=130, height=38, radius=12,
        ).pack(side="left", padx=4)

        columns = (
            "id", "date", "time", "teacher",
            "room", "group", "cost", "status",
        )
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", selectmode="browse"
        )

        headers = [
            ("id", "ID", 50, "center"),
            ("date", "Дата", 100, "center"),
            ("time", "Время", 110, "center"),
            ("teacher", "Преподаватель", 200, "w"),
            ("room", "Кабинет", 140, "w"),
            ("group", "Тип", 90, "center"),
            ("cost", "Стоимость", 100, "e"),
            ("status", "Статус", 110, "center"),
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

        self.tree.bind("<Double-1>", lambda _: self._on_edit())

    def refresh(self) -> None:
        """Обновляет таблицу занятий."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        status_map = {
            "planned": "Запланировано",
            "done": "Проведено",
            "cancelled": "Отменено",
            "paid": "Оплачено",
        }

        for lesson in self.repo.list_all():
            teacher_name = lesson.teacher.full_name if lesson.teacher else "—"
            room_name = lesson.room.name if lesson.room else "—"
            time_start = lesson.time_start.strftime("%H:%M")
            time_end = lesson.time_end.strftime("%H:%M")

            self.tree.insert(
                "",
                "end",
                iid=str(lesson.id),
                values=(
                    lesson.id,
                    lesson.date.isoformat(),
                    f"{time_start}–{time_end}",
                    teacher_name,
                    room_name,
                    "Групповое" if lesson.is_group else "Индивид.",
                    f"{lesson.cost:.2f}",
                    status_map.get(lesson.status, lesson.status),
                ),
            )

    def _get_selected(self) -> Lesson | None:
        """Возвращает выбранное занятие или None."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Информация", "Выберите занятие в таблице", parent=self
            )
            return None
        return self.repo.get(int(selection[0]))

    def _on_add(self) -> None:
        form = LessonForm(self, self.session)
        self.wait_window(form)
        if form.result is not None:
            self.refresh()

    def _on_edit(self) -> None:
        lesson = self._get_selected()
        if lesson is None:
            return
        form = LessonForm(self, self.session, lesson=lesson)
        self.wait_window(form)
        if form.result is not None:
            self.refresh()

    def _on_mark_done(self) -> None:
        lesson = self._get_selected()
        if lesson is None:
            return
        try:
            self.repo.mark_done(lesson.id)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def _on_cancel(self) -> None:
        lesson = self._get_selected()
        if lesson is None:
            return
        try:
            self.repo.cancel(lesson.id)
            self.refresh()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def _on_delete(self) -> None:
        lesson = self._get_selected()
        if lesson is None:
            return
        if not messagebox.askyesno(
            "Подтверждение",
            f"Удалить занятие id={lesson.id}?",
            parent=self,
        ):
            return
        try:
            self.repo.delete(lesson.id)
            self.refresh()
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Ошибка", str(e), parent=self)
