"""Экран «Отчёты»: сводка и экспорт данных."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from sqlalchemy.orm import Session

from src.services.report_service import ReportService
from src.ui import theme
from src.ui.widgets import RoundedButton


class ReportsView(ttk.Frame):
    """Экран отчётов и экспорта.

    Attributes:
        session: Сессия SQLAlchemy.
        service: Сервис отчётов.
    """

    def __init__(self, parent: tk.Widget, session: Session) -> None:
        """Инициализирует экран.

        Args:
            parent: Родительский виджет.
            session: Сессия SQLAlchemy.
        """
        super().__init__(parent)
        self.session = session
        self.service = ReportService(session)

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Создаёт таблицу сводки и кнопки экспорта."""
        columns = ("metric", "value")
        self.tree = ttk.Treeview(
            self, columns=columns, show="headings", height=10
        )
        self.tree.heading("metric", text="Показатель")
        self.tree.heading("value", text="Значение")
        self.tree.column("metric", width=400, anchor="w")
        self.tree.column("value", width=300, anchor="e")
        self.tree.pack(fill="both", expand=True, pady=(0, 20))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")

        RoundedButton(
            btn_frame, text="Ученики → CSV", command=self._export_students_csv,
            width=180, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            btn_frame, text="Занятия → CSV", command=self._export_lessons_csv,
            width=180, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            btn_frame, text="Все данные → JSON", command=self._export_full_json,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=200, height=38, radius=12,
        ).pack(side="left", padx=4)

        RoundedButton(
            btn_frame, text="Обновить", command=self.refresh,
            bg_color=theme.COLORS["accent"],
            fg_color=theme.COLORS["text"],
            border_color=theme.COLORS["accent_hover"],
            hover_color=theme.COLORS["accent_hover"],
            width=140, height=38, radius=12,
        ).pack(side="left", padx=4)

    def refresh(self) -> None:
        """Обновляет таблицу сводки."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        summary = self.service.get_income_summary()

        rows = [
            ("Учеников в базе", str(summary["students_count"])),
            ("Преподавателей в базе", str(summary["teachers_count"])),
            ("Занятий в базе", str(summary["lessons_count"])),
            ("Общий доход (сумма платежей)", f"{summary['total_income']} ₽"),
            ("Общая сумма выплат", f"{summary['total_payouts']} ₽"),
            ("Неоплаченные выплаты", f"{summary['unpaid_payouts']} ₽"),
            (
                "Чистая прибыль",
                f"{summary['total_income'] - summary['total_payouts']} ₽",
            ),
        ]

        for metric, value in rows:
            self.tree.insert("", "end", values=(metric, value))

    def _export_students_csv(self) -> None:
        """Экспортирует учеников в CSV."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
            initialfile="students.csv",
            parent=self,
        )
        if not file_path:
            return
        try:
            count = self.service.export_students_csv(Path(file_path))
            messagebox.showinfo(
                "Экспорт", f"Экспортировано записей: {count}", parent=self
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def _export_lessons_csv(self) -> None:
        """Экспортирует занятия в CSV."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv")],
            initialfile="lessons.csv",
            parent=self,
        )
        if not file_path:
            return
        try:
            count = self.service.export_lessons_csv(Path(file_path))
            messagebox.showinfo(
                "Экспорт", f"Экспортировано записей: {count}", parent=self
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)

    def _export_full_json(self) -> None:
        """Экспортирует все данные в JSON."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json")],
            initialfile="studio_export.json",
            parent=self,
        )
        if not file_path:
            return
        try:
            self.service.export_full_json(Path(file_path))
            messagebox.showinfo(
                "Экспорт", "Все данные экспортированы в JSON", parent=self
            )
        except Exception as e:
            messagebox.showerror("Ошибка", str(e), parent=self)
