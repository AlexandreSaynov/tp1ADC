from db.init_db import init_db
from app.auth import AuthService
from db.db_controller import DBController
from app.menus import menu_loop


def main():
    init_db(seed=False)

    db = DBController()
    auth = AuthService(db)
    
    try:
        menu_loop(auth, db)
    finally:
        auth.close()
        db.close()


if __name__ == "__main__":
    main()
