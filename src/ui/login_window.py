"""Окно входа в приложение StudioManager."""
import tkinter as tk
from tkinter import messagebox, ttk

from src.auth import CurrentUser, authenticate
from src.ui import theme
from src.ui.widgets import RoundedButton


# ─── Тестовые аккаунты для быстрого входа ───────────────────
DEMO_ACCOUNTS = [
    ("admin", "admin123", "администратор"),
    ("teacher", "teacher123", "преподаватель"),
    ("student", "student123", "ученик"),
]


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
        self.geometry("460x740")
        self.resizable(False, False)

        theme.apply_theme(self)

        self._build_ui()
        self._center()

    def _build_ui(self) -> None:
        """Создаёт форму входа."""
        header = ttk.Frame(self, style="Sidebar.TFrame", height=130)
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

        # Логин
        ttk.Label(form, text="Логин:").pack(anchor="w", pady=(0, 8))
        self.username_var = tk.StringVar(value="admin")
        username_entry = ttk.Entry(
            form, textvariable=self.username_var, width=40
        )
        username_entry.pack(fill="x", pady=(0, 20))

        # Пароль
        ttk.Label(form, text="Пароль:").pack(anchor="w", pady=(0, 8))
        self.password_var = tk.StringVar(value="admin123")
        password_entry = ttk.Entry(
            form, textvariable=self.password_var, width=40, show="●"
        )
        password_entry.pack(fill="x", pady=(0, 30))

        # ─── Кнопка входа (скруглённая) ─────────────────────
        btn = RoundedButton(
            form,
            text="Войти",
            command=self._on_login,
            width=360,
            height=48,
            radius=14,
            font_size=12,
        )
        btn.pack(pady=(0, 10))

        # ─── Тестовые аккаунты (кликабельные) ───────────────
        ttk.Label(
            form,
            text="Быстрый вход (нажмите на строку):",
            style="Subheader.TLabel",
        ).pack(anchor="w", pady=(25, 10))

        for username, password, role_name in DEMO_ACCOUNTS:
            self._make_demo_link(form, username, password, role_name)

        self.bind("<Return>", lambda _: self._on_login())
        username_entry.focus_set()

    def _make_demo_link(
        self,
        parent: tk.Widget,
        username: str,
        password: str,
        role_name: str,
    ) -> None:
        """Создаёт кликабельную ссылку для быстрого входа.

        Args:
            parent: Родительский виджет.
            username: Логин.
            password: Пароль.
            role_name: Название роли (для отображения).
        """
        text = f"{username} / {password} — {role_name}"
        label = tk.Label(
            parent,
            text=text,
            font=(theme.FONT, 11, "underline"),
            fg=theme.COLORS["primary_hover"],
            bg=theme.COLORS["bg"],
            cursor="hand2",
            anchor="w",
        )
        label.pack(anchor="w", pady=2)

        # Клик — заполнить поля и войти
        def on_click(_event: tk.Event) -> None:
            self.username_var.set(username)
            self.password_var.set(password)
            self._on_login()

        # Наведение — подсветка
        def on_enter(_event: tk.Event) -> None:
            label.configure(fg=theme.COLORS["primary_pressed"])

        def on_leave(_event: tk.Event) -> None:
            label.configure(fg=theme.COLORS["primary_hover"])

        label.bind("<Button-1>", on_click)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

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
