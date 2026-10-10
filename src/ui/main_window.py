"""Главное окно приложения StudioManager (Tkinter)."""
import tkinter as tk
from tkinter import ttk

from src import config
from src.ui import theme


class MainWindow(tk.Tk):
    """Главное окно приложения с боковой панелью навигации.

    Attributes:
        sidebar: Фрейм с кнопками навигации.
        content: Фрейм, в котором отображается текущий экран.
        buttons: Словарь {название: кнопка} для подсветки активной.
    """

    def __init__(self) -> None:
        """Инициализирует окно, размеры и тему."""
        super().__init__()
        self.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1024, 700)

        theme.apply_theme(self)

        self._build_layout()
        self._show_section("Ученики")

    def _build_layout(self) -> None:
        """Создаёт боковую панель и рабочую область."""
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # ─── Левая панель навигации ─────────────────────────
        self.sidebar = ttk.Frame(
            container, width=220, style="Sidebar.TFrame"
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        title = ttk.Label(
            self.sidebar,
            text="StudioManager",
            style="SidebarTitle.TLabel",
        )
        title.pack(fill="x")

        ttk.Separator(self.sidebar, orient="horizontal").pack(
            fill="x", pady=(0, 10)
        )

        sections = [
            "Ученики",
            "Преподаватели",
            "Занятия",
            "Расписание",
            "Финансы",
            "Отчёты",
        ]

        self.buttons: dict[str, ttk.Button] = {}
        for name in sections:
            btn = ttk.Button(
                self.sidebar,
                text=f"  {name}",
                style="Sidebar.TButton",
                command=lambda n=name: self._show_section(n),
            )
            btn.pack(fill="x", padx=0, pady=1)
            self.buttons[name] = btn

        # ─── Правая рабочая область ─────────────────────────
        self.content = ttk.Frame(container, padding=30)
        self.content.pack(side="left", fill="both", expand=True)

    def _show_section(self, name: str) -> None:
        """Показывает экран раздела.

        Args:
            name: Название раздела.
        """
        for section_name, button in self.buttons.items():
            if section_name == name:
                button.configure(style="SidebarActive.TButton")
            else:
                button.configure(style="Sidebar.TButton")

        for widget in self.content.winfo_children():
            widget.destroy()

        ttk.Label(
            self.content,
            text=name,
            style="Header.TLabel",
        ).pack(anchor="w", pady=(0, 20))

        if name == "Ученики":
            self._show_students()
        elif name == "Преподаватели":
            self._show_teachers()
        elif name == "Занятия":
            self._show_lessons()
        elif name == "Расписание":
            self._show_schedule()
        elif name == "Финансы":
            self._show_finance()
        elif name == "Отчёты":
            self._show_reports()
        else:
            ttk.Label(
                self.content,
                text=f"Раздел «{name}» в разработке",
                style="Subheader.TLabel",
            ).pack(anchor="w")

    def _show_students(self) -> None:
        """Подключает экран «Ученики» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.students_view import StudentsView

        session = SessionLocal()
        view = StudentsView(self.content, session)
        view.pack(fill="both", expand=True)

    def _show_teachers(self) -> None:
        """Подключает экран «Преподаватели» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.teachers_view import TeachersView

        session = SessionLocal()
        view = TeachersView(self.content, session)
        view.pack(fill="both", expand=True)

    def _show_lessons(self) -> None:
        """Подключает экран «Занятия» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.lessons_view import LessonsView

        session = SessionLocal()
        view = LessonsView(self.content, session)
        view.pack(fill="both", expand=True)

    def _show_schedule(self) -> None:
        """Подключает экран «Расписание» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.schedule_view import ScheduleView

        session = SessionLocal()
        view = ScheduleView(self.content, session)
        view.pack(fill="both", expand=True)

    def _show_finance(self) -> None:
        """Подключает экран «Финансы» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.finance_view import FinanceView

        session = SessionLocal()
        view = FinanceView(self.content, session)
        view.pack(fill="both", expand=True)

    def _show_reports(self) -> None:
        """Подключает экран «Отчёты» с сессией БД."""
        from src.db.database import SessionLocal
        from src.ui.views.reports_view import ReportsView

        session = SessionLocal()
        view = ReportsView(self.content, session)
        view.pack(fill="both", expand=True)


def run() -> None:
    """Запускает главное окно."""
    app = MainWindow()
    app.mainloop()
