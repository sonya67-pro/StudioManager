"""Экран «Расписание»: занятость кабинетов на дату."""
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.repositories.lesson_repo import LessonRepository


class ScheduleView(ttk.Frame):
    """Экран расписания кабинетов.

    Attributes:
        session: Сессия SQLAlchemy.
        repo: Репозиторий занятий.
        date_var: Строка с выбранной датой.
        tree: Таблица занятий.
    """

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
        """Создаёт панель выбора даты и таблицу."""
        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 10))

        ttk.Label(top, text="Дата (ГГГГ-ММ-ДД):").pack(side="left")

        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(top, textvariable=self.date_var, width=15).pack(
            side="left", padx=(5, 15)
        )

        ttk.Button(top, text="Показать", command=self.refresh).pack(
            side="left", padx=2
        )
        ttk.Button(top, text="Сегодня", command=self._set_today).pack(
            side="left", padx=2
        )

        columns = ("time", "room", "teacher", "group", "status")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", selectmode="browse"
        )

        headers = [
            ("time", "Время", 130, "center"),
            ("room", "Кабинет", 200, "w"),
            ("teacher", "Преподаватель", 250, "w"),
            ("group", "Тип", 120, "center"),
            ("status", "Статус", 130, "center"),
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

    def _set_today(self) -> None:
        """Устанавливает сегодняшнюю дату в поле."""
        self.date_var.set(date.today().isoformat())
        self.refresh()

    def refresh(self) -> None:
        """Обновляет таблицу занятий на выбранную дату."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            target_date = datetime.strptime(
                self.date_var.get().strip(), "%Y-%m-%d"
            ).date()
        except ValueError:
            messagebox.showwarning(
                "Ошибка",
                "Неверный формат даты. Используйте ГГГГ-ММ-ДД",
                parent=self,
            )
            return

        lessons = self.repo.list_by_date(target_date)

        if not lessons:
            self.tree.insert(
                "",
                "end",
                values=("—", "Нет занятий на эту дату", "", "", ""),
            )
            return

        status_map = {
            "planned": "Запланировано",
            "done": "Проведено",
            "cancelled": "Отменено",
            "paid": "Оплачено",
        }

        for lesson in lessons:
            room_name = lesson.room.name if lesson.room else "—"
            teacher_name = lesson.teacher.full_name if lesson.teacher else "—"
            time_start = lesson.time_start.strftime("%H:%M")
            time_end = lesson.time_end.strftime("%H:%M")

            self.tree.insert(
                "",
                "end",
                iid=str(lesson.id),
                values=(
                    f"{time_start}–{time_end}",
                    room_name,
                    teacher_name,
                    "Групповое" if lesson.is_group else "Индивид.",
                    status_map.get(lesson.status, lesson.status),
                ),
            )
