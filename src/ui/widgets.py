"""Кастомные виджеты для приложения StudioManager.

Содержит RoundedButton — кнопку со скруглёнными углами и обводкой.
"""
import tkinter as tk

from src.ui import theme


class RoundedButton(tk.Canvas):
    """Кнопка со скруглёнными углами и обводкой.

    Attributes:
        text: Текст кнопки.
        command: Функция, вызываемая при клике.
        bg_color: Цвет фона.
        fg_color: Цвет текста.
        border_color: Цвет обводки.
        border_width: Толщина обводки.
        hover_color: Цвет при наведении.
        radius: Радиус скругления.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command=None,
        bg_color: str | None = None,
        fg_color: str = "#ffffff",
        border_color: str | None = None,
        border_width: int = 2,
        hover_color: str | None = None,
        radius: int = 14,
        width: int = 160,
        height: int = 42,
        font_size: int = 11,
    ) -> None:
        """Инициализирует кнопку.

        Args:
            parent: Родительский виджет.
            text: Текст кнопки.
            command: Функция при клике.
            bg_color: Цвет фона (по умолчанию — из темы).
            fg_color: Цвет текста.
            border_color: Цвет обводки (по умолчанию — тёмно-розовый).
            border_width: Толщина обводки.
            hover_color: Цвет при наведении.
            radius: Радиус скругления.
            width: Ширина кнопки.
            height: Высота кнопки.
            font_size: Размер шрифта.
        """
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=theme.COLORS["bg"],
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )

        self.text = text
        self.command = command
        self.bg_color = bg_color or theme.COLORS["primary"]
        self.fg_color = fg_color
        self.border_color = border_color or theme.COLORS["primary_pressed"]
        self.border_width = border_width
        self.hover_color = hover_color or theme.COLORS["primary_hover"]
        self.radius = radius
        self.width = width
        self.height = height
        self.font_size = font_size

        self._draw_button(self.bg_color)

        # Обработчики событий
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw_button(self, color: str) -> None:
        """Рисует скруглённую кнопку с обводкой.

        Args:
            color: Цвет заливки.
        """
        self.delete("all")
        r = self.radius
        w = self.width
        h = self.height
        bw = self.border_width

        # Фон кнопки (чуть больше канваса — чтобы обводка «не резалась»)
        self.create_rectangle(
            0, 0, w, h,
            fill=theme.COLORS["bg"],
            outline=theme.COLORS["bg"],
        )

        # Скруглённый прямоугольник — с обводкой
        # (используем create_polygon со сглаживанием — точнее для обводки)
        self._draw_rounded_rect(
            bw // 2, bw // 2, w - bw // 2, h - bw // 2,
            r, fill=color, outline=self.border_color, width=bw,
        )

        # Текст
        self.create_text(
            w // 2,
            h // 2,
            text=self.text,
            fill=self.fg_color,
            font=(theme.FONT, self.font_size),
        )

    def _draw_rounded_rect(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        r: int,
        fill: str,
        outline: str,
        width: int = 2,
    ) -> None:
        """Рисует скруглённый прямоугольник через polygon.

        Args:
            x1, y1: Верхний левый угол.
            x2, y2: Нижний правый угол.
            r: Радиус скругления.
            fill: Цвет заливки.
            outline: Цвет обводки.
            width: Толщина обводки.
        """
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        self.create_polygon(
            points,
            fill=fill,
            outline=outline,
            width=width,
            smooth=True,
            splinesteps=36,
        )

    def _on_click(self, _event: tk.Event) -> None:
        """Обработчик клика."""
        if self.command:
            self.command()

    def _on_enter(self, _event: tk.Event) -> None:
        """Обработчик наведения."""
        self._draw_button(self.hover_color)

    def _on_leave(self, _event: tk.Event) -> None:
        """Обработчик ухода курсора."""
        self._draw_button(self.bg_color)
