"""Главное окно приложения StudioManager (Tkinter)."""
import tkinter as tk
from tkinter import ttk

from src import config


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

        self._setup_style()
        self._build_layout()
        self._show_section("Ученики")

    def _setup_style(self) -> None:
        """Настраивает стили ttk для единообразного вида."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Sidebar.TButton",
            font=("Segoe UI", 11),
            anchor="w",
            padding=(20, 12),
            borderwidth=0,
        )
        style.configure(
            "SidebarActive.TButton",
            font=("Segoe UI", 11, "bold"),
            anchor="w",
            padding=(20, 12),
            borderwidth=0,
        )
        style.configure(
            "Header.TLabel",
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "Hint.TLabel",
            font=("Segoe UI", 10),
            foreground="gray",
        )

    def _build_layout(self) -> None:
        """Создаёт боковую панель и рабочую область."""
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Левая панель навигации
        self.sidebar = ttk.Frame(container, width=220, padding=(0, 10))
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        title = ttk.Label(
            self.sidebar,
            text="StudioManager",
            font=("Segoe UI", 14, "bold"),
            padding=(20, 10),
        )
        title.pack(fill="x")

        # Разделитель
        ttk.Separator(self.sidebar, orient="horizontal").pack(
            fill="x", pady=(0, 10)
        )

        # Кнопки навигации
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
                text=name,
                style="Sidebar.TButton",
                command=lambda n=name: self._show_section(n),
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.buttons[name] = btn

        # Правая рабочая область
        self.content = ttk.Frame(container, padding=20)
        self.content.pack(side="left", fill="both", expand=True)

    def _show_section(self, name: str) -> None:
        """Показывает экран раздела.

        Args:
            name: Название раздела («Ученики», «Преподаватели» и т.д.).
        """
        # Подсветка активной кнопки
        for section_name, button in self.buttons.items():
            if section_name == name:
                button.configure(style="SidebarActive.TButton")
            else:
                button.configure(style="Sidebar.TButton")

        # Очистить рабочую область
        for widget in self.content.winfo_children():
            widget.destroy()

        # Заголовок раздела
        ttk.Label(
            self.content,
            text=name,
            style="Header.TLabel",
        ).pack(anchor="w", pady=(0, 20))

        # Заглушка — здесь будет экран раздела
        ttk.Label(
            self.content,
            text=f"Раздел «{name}» в разработке",
            style="Hint.TLabel",
        ).pack(anchor="w")


def run() -> None:
    """Запускает главное окно."""
    app = MainWindow()
    app.mainloop()
