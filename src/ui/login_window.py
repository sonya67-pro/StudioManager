"""Окно входа в приложение StudioManager."""
import tkinter as tk
from tkinter import messagebox, ttk

from src.auth import CurrentUser, authenticate
from src.ui import theme


class LoginWindow(tk.Tk):
    """Окно авторизации.

    Attributes:
        user: Авторизованный пользователь (None — если закрыли).
    """

    def __init__(self) -> None:
        """Инициализирует окно входа."""
        super().__init__()
        self.user: CurrentUser | None = None

        self.title("StudioManager — Вход")
        self.geometry("420x620")
        self.resizable(False, False)

        theme.apply_theme(self)

        self._build_ui()
        self._center()

    def _build_ui(self) -> None:
        """Создаёт форму входа."""
        header = ttk.Frame(self, style="Sidebar.TFrame", height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        ttk.Label(
            header,
            text="StudioManager",
            style="SidebarTitle.TLabel",
        ).pack(expand=True)

        form = ttk.Frame(self, padding=40)
        form.pack(fill="both", expand=True)

        ttk.Label(
            form,
            text="Вход в систему",
            style="Header.TLabel",
        ).pack(anchor="w", pady=(0, 5))

        ttk.Label(
            form,
            text="Введите логин и пароль",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(0, 25))

        ttk.Label(form, text="Логин:").pack(anchor="w", pady=(0, 5))
        self.username_var = tk.StringVar(value="admin")
        username_entry = ttk.Entry(
            form, textvariable=self.username_var, width=40
        )
        username_entry.pack(fill="x", pady=(0, 15))

        ttk.Label(form, text="Пароль:").pack(anchor="w", pady=(0, 5))
        self.password_var = tk.StringVar(value="admin123")
        password_entry = ttk.Entry(
            form, textvariable=self.password_var, width=40, show="●"
        )
        password_entry.pack(fill="x", pady=(0, 25))

        ttk.Button(
            form, text="Войти", command=self._on_login
        ).pack(fill="x")

        ttk.Label(
            form,
            text="Тестовые аккаунты:\n"
                 "admin / admin123 — администратор\n"
                 "teacher / teacher123 — преподаватель\n"
                 "student / student123 — ученик",
            style="Subheader.TLabel",
            justify="left",
        ).pack(anchor="w", pady=(20, 0))

        self.bind("<Return>", lambda _: self._on_login())
        username_entry.focus_set()

    def _on_login(self) -> None:
        """Проверяет логин и пароль, авторизует пользователя."""
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning(
                "Ошибка", "Введите логин и пароль", parent=self
            )
            return

        user = authenticate(username, password)
        if user is None:
            messagebox.showerror(
                "Ошибка",
                "Неверный логин или пароль",
                parent=self,
            )
            return

        self.user = user
        self.destroy()

    def _center(self) -> None:
        """Центрирует окно на экране."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")
