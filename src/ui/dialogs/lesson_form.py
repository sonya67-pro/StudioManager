"""Модальная форма для добавления/редактирования занятия."""
import tkinter as tk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

from sqlalchemy.orm import Session

from src.db.models import Lesson
from src.repositories.lesson_repo import LessonRepository
from src.repositories.room_repo import RoomRepository
from src.repositories.teacher_repo import TeacherRepository


class LessonForm(tk.Toplevel):
    """Диалог для создания или редактирования занятия.

    Attributes:
        session: Сессия SQLAlchemy.
        lesson: Редактируемое занятие (None — создание).
        result: Созданное/обновлённое занятие после закрытия.
    """

    def __init__(
        self,
        parent: tk.Widget,
        session: Session,
        lesson: Lesson | None = None,
    ) -> None:
        """Инициализирует форму.

        Args:
            parent: Родительское окно.
            session: Сессия SQLAlchemy.
            lesson: Занятие для редактирования (None — создание).
        """
        super().__init__(parent)
        self.session = session
        self.lesson = lesson
        self.result: Lesson | None = None

        self.title("Редактирование занятия" if lesson else "Новое занятие")
        self.geometry("480x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center(parent)

    def _build_ui(self) -> None:
        """Создаёт поля формы."""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Преподаватель
        ttk.Label(frame, text="Преподаватель:").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.teacher_var = tk.StringVar()
        self.teacher_combo = ttk.Combobox(
            frame, textvariable=self.teacher_var, state="readonly", width=37
        )
        self.teacher_combo.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )
        self._load_teachers()

        # Кабинет
        ttk.Label(frame, text="Кабинет:").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(
            frame, textvariable=self.room_var, state="readonly", width=37
        )
        self.room_combo.grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )
        self._load_rooms()

        # Дата
        ttk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        self.date_var = tk.StringVar(
            value=self.lesson.date.isoformat() if self.lesson else ""
        )
        ttk.Entry(frame, textvariable=self.date_var, width=40).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # Время начала и конца (в одной строке)
        time_frame = ttk.Frame(frame)
        time_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        time_frame.columnconfigure(0, weight=1)
        time_frame.columnconfigure(1, weight=1)

        ttk.Label(time_frame, text="Начало (ЧЧ:ММ):").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.start_var = tk.StringVar(
            value=self.lesson.time_start.strftime("%H:%M") if self.lesson else "10:00"
        )
        ttk.Entry(time_frame, textvariable=self.start_var, width=15).grid(
            row=1, column=0, sticky="ew", padx=(0, 5)
        )

        ttk.Label(time_frame, text="Конец (ЧЧ:ММ):").grid(
            row=0, column=1, sticky="w", pady=(0, 5)
        )
        self.end_var = tk.StringVar(
            value=self.lesson.time_end.strftime("%H:%M") if self.lesson else "11:00"
        )
        ttk.Entry(time_frame, textvariable=self.end_var, width=15).grid(
            row=1, column=1, sticky="ew"
        )

        # Стоимость
        ttk.Label(frame, text="Стоимость, ₽:").grid(
            row=7, column=0, sticky="w", pady=(0, 5)
        )
        self.cost_var = tk.StringVar(
            value=str(self.lesson.cost) if self.lesson else "1000.00"
        )
        ttk.Entry(frame, textvariable=self.cost_var, width=40).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # Групповое
        self.is_group_var = tk.BooleanVar(
            value=bool(self.lesson.is_group) if self.lesson else False
        )
        ttk.Checkbutton(
            frame,
            text="Групповое занятие",
            variable=self.is_group_var,
        ).grid(row=9, column=0, sticky="w", pady=(0, 15))

        # Кнопки
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=10, column=0, columnspan=2, pady=(10, 0), sticky="e")

        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(
            side="right", padx=(10, 0)
        )
        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(
            side="right"
        )

    def _load_teachers(self) -> None:
        """Загружает список преподавателей в комбобокс."""
        repo = TeacherRepository(self.session)
        self._teachers = repo.list_all()
        self._teacher_map = {f"{t.id}: {t.full_name}": t.id for t in self._teachers}
        self.teacher_combo["values"] = list(self._teacher_map.keys())

        if self.lesson:
            for label, tid in self._teacher_map.items():
                if tid == self.lesson.teacher_id:
                    self.teacher_var.set(label)
                    break
        elif self._teachers:
            self.teacher_var.set(list(self._teacher_map.keys())[0])

    def _load_rooms(self) -> None:
        """Загружает список кабинетов в комбобокс."""
        repo = RoomRepository(self.session)
        self._rooms = repo.list_all()
        self._room_map = {f"{r.id}: {r.name}": r.id for r in self._rooms}
        self.room_combo["values"] = list(self._room_map.keys())

        if self.lesson:
            for label, rid in self._room_map.items():
                if rid == self.lesson.room_id:
                    self.room_var.set(label)
                    break
        elif self._rooms:
            self.room_var.set(list(self._room_map.keys())[0])

    def _save(self) -> None:
        """Сохраняет занятие в БД."""
        if not self.teacher_var.get() or not self.room_var.get():
            messagebox.showwarning(
                "Ошибка", "Выберите преподавателя и кабинет", parent=self
            )
            return

        try:
            lesson_date = datetime.strptime(
                self.date_var.get().strip(), "%Y-%m-%d"
            ).date()
            time_start = datetime.strptime(
                self.start_var.get().strip(), "%H:%M"
            ).time()
            time_end = datetime.strptime(
                self.end_var.get().strip(), "%H:%M"
            ).time()
            cost = Decimal(self.cost_var.get().strip())
        except (ValueError, InvalidOperation):
            messagebox.showwarning(
                "Ошибка",
                "Проверьте формат даты, времени и стоимости",
                parent=self,
            )
            return

        if time_end <= time_start:
            messagebox.showwarning(
                "Ошибка", "Конец должен быть позже начала", parent=self
            )
            return

        if cost <= 0:
            messagebox.showwarning(
                "Ошибка", "Стоимость должна быть положительной", parent=self
            )
            return

        teacher_id = self._teacher_map[self.teacher_var.get()]
        room_id = self._room_map[self.room_var.get()]

        try:
            if self.lesson:
                self.lesson.teacher_id = teacher_id
                self.lesson.room_id = room_id
                self.lesson.date = lesson_date
                self.lesson.time_start = time_start
                self.lesson.time_end = time_end
                self.lesson.cost = cost
                self.lesson.is_group = 1 if self.is_group_var.get() else 0
                self.session.commit()
                self.session.refresh(self.lesson)
                self.result = self.lesson
            else:
                repo = LessonRepository(self.session)
                self.result = repo.add(
                    teacher_id=teacher_id,
                    room_id=room_id,
                    lesson_date=lesson_date,
                    time_start=time_start,
                    time_end=time_end,
                    cost=cost,
                    is_group=self.is_group_var.get(),
                )
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Ошибка", str(e), parent=self)
            return

        self.destroy()

    def _center(self, parent: tk.Widget) -> None:
        """Центрирует диалог относительно родителя."""
        self.update_idletasks()
        px = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        py = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")
