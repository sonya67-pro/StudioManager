"""Цветовая схема и стили приложения StudioManager.

Тема: современная светлая с серым фоном и зелёным акцентом,
с элементами «стеклянного» дизайна (мягкие тени, светлые панели).
"""
import tkinter as tk
from tkinter import ttk


# ─── Цветовая палитра (серый + зелёный + стекло) ─────────────
COLORS = {
    # Фоны — светлые серые (имитация стекла)
    "bg": "#f0f2f5",              # основной фон окна
    "surface": "#fafbfc",         # панели / карточки (чуть светлее)
    "surface_alt": "#e8eaed",     # альтернативный фон

    # Боковая панель — полупрозрачный серый
    "sidebar_bg": "#2d3748",      # тёмно-серый (стекло)
    "sidebar_bg_light": "#384453",  # для hover
    "sidebar_fg": "#e2e8f0",      # текст в sidebar
    "sidebar_fg_muted": "#a0aec0",  # приглушённый текст

    # Акценты — зелёный (как в iOS success / modern UI)
    "primary": "#10b981",         # основной зелёный
    "primary_hover": "#059669",   # тёмнее (hover)
    "primary_light": "#d1fae5",   # светло-зелёный фон
    "accent": "#34d399",          # яркий зелёный акцент

    # Дополнительные статусы
    "danger": "#ef4444",          # красный (удаление)
    "danger_hover": "#dc2626",
    "warning": "#f59e0b",         # оранжевый (внимание)
    "info": "#3b82f6",            # синий (информация)

    # Текст
    "text": "#1f2937",            # основной тёмный
    "text_muted": "#6b7280",      # серый текст
    "text_light": "#9ca3af",      # очень светлый

    # Границы и разделители
    "border": "#e5e7eb",          # светлая граница
    "border_strong": "#d1d5db",   # потемнее

    # Строки таблиц
    "row_alt": "#f9fafb",         # чередование строк

    # Тени / стекло (имитация)
    "shadow": "#d1d5db",          # «тень» под панелями
    "glass": "#ffffff",           # светлый верхний слой
}


def apply_theme(root: tk.Tk) -> None:
    """Применяет стили ко всему приложению.

    Args:
        root: Корневое окно Tk.
    """
    root.configure(bg=COLORS["bg"])

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # ─── Общие настройки ────────────────────────────────────
    style.configure(
        ".",
        font=("Segoe UI", 10),
        background=COLORS["bg"],
        foreground=COLORS["text"],
    )
    style.configure("TFrame", background=COLORS["bg"])
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
    )

    # Панель-«стекло» (светлая карточка)
    style.configure(
        "Surface.TFrame",
        background=COLORS["surface"],
        relief="flat",
        borderwidth=0,
    )
    style.configure(
        "Surface.TLabel",
        background=COLORS["surface"],
        foreground=COLORS["text"],
    )

    # ─── Заголовки ──────────────────────────────────────────
    style.configure(
        "Header.TLabel",
        font=("Segoe UI", 22, "bold"),
        foreground=COLORS["text"],
        background=COLORS["bg"],
    )
    style.configure(
        "Subheader.TLabel",
        font=("Segoe UI", 11),
        foreground=COLORS["text_muted"],
        background=COLORS["bg"],
    )

    # ─── Боковая панель (тёмно-серая «стеклянная») ──────────
    style.configure(
        "Sidebar.TFrame",
        background=COLORS["sidebar_bg"],
        relief="flat",
        borderwidth=0,
    )
    style.configure(
        "SidebarTitle.TLabel",
        font=("Segoe UI", 16, "bold"),
        foreground="#ffffff",
        background=COLORS["sidebar_bg"],
        padding=(20, 20),
    )
    style.configure(
        "Sidebar.TButton",
        font=("Segoe UI", 11),
        anchor="w",
        padding=(20, 14),
        borderwidth=0,
        relief="flat",
        background=COLORS["sidebar_bg"],
        foreground=COLORS["sidebar_fg"],
    )
    style.map(
        "Sidebar.TButton",
        background=[
            ("active", COLORS["sidebar_bg_light"]),
            ("pressed", COLORS["primary"]),
        ],
        foreground=[("active", "#ffffff")],
    )
    style.configure(
        "SidebarActive.TButton",
        font=("Segoe UI", 11, "bold"),
        anchor="w",
        padding=(20, 14),
        borderwidth=0,
        relief="flat",
        background=COLORS["primary"],
        foreground="#ffffff",
    )
    style.map(
        "SidebarActive.TButton",
        background=[
            ("active", COLORS["primary_hover"]),
            ("pressed", COLORS["primary_hover"]),
        ],
    )

    # ─── Обычные кнопки (зелёные) ───────────────────────────
    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(14, 8),
        borderwidth=0,
        relief="flat",
        background=COLORS["primary"],
        foreground="#ffffff",
        focuscolor=COLORS["primary"],
    )
    style.map(
        "TButton",
        background=[
            ("active", COLORS["primary_hover"]),
            ("pressed", COLORS["primary_hover"]),
            ("disabled", COLORS["border"]),
        ],
        foreground=[
            ("disabled", COLORS["text_light"]),
            ("active", "#ffffff"),
        ],
    )

    # Кнопка-«опасность» (красная)
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="#ffffff",
    )
    style.map(
        "Danger.TButton",
        background=[
            ("active", COLORS["danger_hover"]),
            ("pressed", COLORS["danger_hover"]),
        ],
    )

    # Кнопка-«призрак» (серая, для второстепенных действий)
    style.configure(
        "Ghost.TButton",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        borderwidth=0,
    )
    style.map(
        "Ghost.TButton",
        background=[
            ("active", COLORS["border"]),
            ("pressed", COLORS["border_strong"]),
        ],
    )

    # ─── Поля ввода ─────────────────────────────────────────
    style.configure(
        "TEntry",
        font=("Segoe UI", 10),
        padding=8,
        fieldbackground=COLORS["glass"],
        foreground=COLORS["text"],
        bordercolor=COLORS["border"],
        lightcolor=COLORS["border"],
        darkcolor=COLORS["border"],
        insertcolor=COLORS["text"],
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", COLORS["primary"])],
        lightcolor=[("focus", COLORS["primary"])],
        darkcolor=[("focus", COLORS["primary"])],
    )

    style.configure(
        "TCombobox",
        padding=6,
        fieldbackground=COLORS["glass"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["text_muted"],
        bordercolor=COLORS["border"],
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["glass"])],
        bordercolor=[("focus", COLORS["primary"])],
    )

    # ─── Таблица (Treeview) — «стеклянная» ──────────────────
    style.configure(
        "Treeview",
        font=("Segoe UI", 10),
        rowheight=32,
        background=COLORS["glass"],
        fieldbackground=COLORS["glass"],
        foreground=COLORS["text"],
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        padding=(10, 10),
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "Treeview.Heading",
        background=[("active", COLORS["border"])],
        foreground=[("active", COLORS["text"])],
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["primary_light"])],
        foreground=[("selected", COLORS["text"])],
    )

    # ─── Разделитель ────────────────────────────────────────
    style.configure(
        "TSeparator",
        background=COLORS["sidebar_bg_light"],
    )

    # ─── LabelFrame (карточки) ──────────────────────────────
    style.configure(
        "TLabelframe",
        background=COLORS["surface"],
        bordercolor=COLORS["border"],
        relief="flat",
        borderwidth=1,
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10, "bold"),
    )

    # ─── Checkbutton ────────────────────────────────────────
    style.configure(
        "TCheckbutton",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
    style.map(
        "TCheckbutton",
        background=[("active", COLORS["bg"])],
    )
