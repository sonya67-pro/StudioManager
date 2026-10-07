"""Главное окно приложения StudioManager (Tkinter)."""

import tkinter as tk
from tkinter import ttk

from src import config


class MainWindow(tk.Tk):
    """Главное окно приложения."""

    def __init__(self) -> None:
        """Инициализирует окно, размеры и заголовок."""
        super().__init__()
        self.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.geometry("1280x800")
        self.minsize(1024, 700)
        self._build_layout()

    def _build_layout(self) -> None:
        """Создаёт базовую разметку окна."""
        ttk.Label(
            self,
            text="StudioManager — учёт занятий студии",
            font=("Segoe UI", 20, "bold"),
        ).pack(pady=20)

        ttk.Label(
            self,
            text="Здесь будет интерфейс по макетам из Figma",
            font=("Segoe UI", 12),
        ).pack(pady=10)


def run() -> None:
    """Запускает главное окно приложения."""
    app = MainWindow()
    app.mainloop()
