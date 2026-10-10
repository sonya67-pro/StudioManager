"""Точка входа приложения StudioManager."""
from src.db.database import init_db


def main() -> None:
    """Инициализирует БД и запускает окно входа."""
    init_db()

    from src.ui.login_window import LoginWindow
    from src.ui.main_window import MainWindow

    login = LoginWindow()
    login.mainloop()

    if login.user is None:
        return

    app = MainWindow(user=login.user)
    app.mainloop()


if __name__ == "__main__":
    main()
