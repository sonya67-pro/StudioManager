"""Репозиторий для работы с кабинетами (таблица rooms)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import Room


class RoomRepository:
    """CRUD-операции над кабинетами.

    Attributes:
        session: Активная сессия SQLAlchemy.
    """

    def __init__(self, session: Session) -> None:
        """Инициализирует репозиторий с заданной сессией.

        Args:
            session: Сессия SQLAlchemy для работы с БД.
        """
        self.session = session

    def add(self, name: str, capacity: int = 1) -> Room:
        """Создаёт новый кабинет.

        Args:
            name: Название/номер кабинета (уникально).
            capacity: Вместимость (сколько человек помещается).

        Returns:
            Созданный объект Room с присвоенным id.
        """
        room = Room(name=name, capacity=capacity)
        self.session.add(room)
        self.session.commit()
        self.session.refresh(room)
        return room

    def get(self, room_id: int) -> Room | None:
        """Возвращает кабинет по id или None, если не найден.

        Args:
            room_id: Первичный ключ кабинета.

        Returns:
            Объект Room или None.
        """
        return self.session.get(Room, room_id)

    def list_all(self) -> list[Room]:
        """Возвращает список всех кабинетов, отсортированный по id.

        Returns:
            Список объектов Room.
        """
        statement = select(Room).order_by(Room.id)
        return list(self.session.scalars(statement).all())

    def find_by_name(self, query: str) -> list[Room]:
        """Ищет кабинеты по подстроке в названии (регистронезависимо).

        Args:
            query: Строка поиска.

        Returns:
            Список подходящих кабинетов.
        """
        query_lower = query.lower()
        return [
            room
            for room in self.list_all()
            if query_lower in room.name.lower()
        ]

    def update(self, room_id: int, name: str, capacity: int) -> Room:
        """Обновляет название и вместимость кабинета.

        Args:
            room_id: ID кабинета.
            name: Новое название.
            capacity: Новая вместимость.

        Returns:
            Обновлённый объект Room.

        Raises:
            ValueError: Если кабинет не найден или вместимость меньше 1.
        """
        if capacity < 1:
            raise ValueError("Вместимость должна быть не меньше 1")

        room = self.get(room_id)
        if room is None:
            raise ValueError(f"Кабинет с id={room_id} не найден")

        room.name = name
        room.capacity = capacity
        self.session.commit()
        self.session.refresh(room)
        return room

    def delete(self, room_id: int) -> bool:
        """Удаляет кабинет по id.

        Args:
            room_id: ID кабинета.

        Returns:
            True, если кабинет был удалён, иначе False.
        """
        room = self.get(room_id)
        if room is None:
            return False
        self.session.delete(room)
        self.session.commit()
        return True
