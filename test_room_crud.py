"""Проверка CRUD-операций через RoomRepository."""
from src.db.database import get_session, init_db
from src.repositories.room_repo import RoomRepository


def main() -> None:
    """Демонстрирует работу CRUD-репозитория кабинетов."""
    init_db()
    print("=== Проверка CRUD кабинетов ===\n")

    with get_session() as session:
        repo = RoomRepository(session)

        # CREATE
        print("1. Добавляем три кабинета...")
        room_1 = repo.add("Кабинет №1 — фортепиано", capacity=2)
        room_2 = repo.add("Кабинет №2 — вокал", capacity=1)
        room_3 = repo.add("Кабинет №3 — групповой", capacity=6)
        print(f"   Создано: {room_1.name}, {room_2.name}, {room_3.name}\n")

        # READ (все)
        print("2. Список всех кабинетов:")
        for room in repo.list_all():
            print(f"   [{room.id}] {room.name} — вместимость {room.capacity}")
        print()

        # READ (поиск)
        print("3. Поиск по 'вокал':")
        for room in repo.find_by_name("вокал"):
            print(f"   [{room.id}] {room.name}")
        print()

        # UPDATE
        print("4. Меняем кабинет №1: вместимость 4...")
        room_1 = repo.update(
            room_1.id, name="Кабинет №1 — фортепиано (обновлён)", capacity=4
        )
        print(f"   Новое название: {room_1.name}, вместимость: {room_1.capacity}\n")

        # DELETE
        print("5. Удаляем кабинет №2...")
        deleted = repo.delete(room_2.id)
        print(f"   Удалён: {deleted}\n")

        print("6. Итоговый список:")
        for room in repo.list_all():
            print(f"   [{room.id}] {room.name} — вместимость {room.capacity}")

    print("\n=== Проверка завершена ===")


if __name__ == "__main__":
    main()
