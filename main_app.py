from db.init_db import init_db
from auth import AuthService
from db.db_controller import DBController
#from menus import menu_loop


def main():
    init_db(seed=False)

    auth = AuthService()
    db = DBController()

    try:
        #To be developed
        #menu_loop(auth, db)
        print("menu")
    finally:
        auth.close()
        db.close()


if __name__ == "__main__":
    main()
