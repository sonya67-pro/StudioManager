"""Простая авторизация пользователей (логин/пароль из констант).

В учебном проекте пароли хранятся в коде. В production-версии
их надо хранить в БД с хэшированием (bcrypt/argon2).
"""
from dataclasses import dataclass


USERS: dict[str, dict] = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "name": "Администратор",
    },
    "teacher": {
        "password": "teacher123",
        "role": "teacher",
        "name": "Преподаватель",
    },
    "student": {
        "password": "student123",
        "role": "student",
        "name": "Ученик",
    },
}


ROLE_ACCESS: dict[str, list[str]] = {
    "admin": [
        "Ученики",
        "Преподаватели",
        "Занятия",
        "Расписание",
        "Финансы",
        "Отчёты",
    ],
    "teacher": [
        "Расписание",
        "Отчёты",
    ],
    "student": [
        "Расписание",
    ],
}


@dataclass
class CurrentUser:
    """Текущий авторизованный пользователь.

    Attributes:
        username: Логин.
        role: Роль (admin / teacher / student).
        name: Отображаемое имя.
    """

    username: str
    role: str
    name: str

    def can_access(self, section: str) -> bool:
        """Проверяет, доступен ли пользователю раздел.

        Args:
            section: Название раздела («Ученики», «Расписание» и т.д.).

        Returns:
            True, если раздел доступен.
        """
        return section in ROLE_ACCESS.get(self.role, [])


def authenticate(username: str, password: str) -> CurrentUser | None:
    """Проверяет логин и пароль.

    Args:
        username: Логин.
        password: Пароль.

    Returns:
        CurrentUser при успехе, None при ошибке.
    """
    user_data = USERS.get(username.strip().lower())
    if user_data is None:
        return None
    if user_data["password"] != password:
        return None
    return CurrentUser(
        username=username.strip().lower(),
        role=user_data["role"],
        name=user_data["name"],
    )
