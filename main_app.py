from app.permissions import PermissionManager
from app.auth import AuthService
from db.db_controller import DBController
import db.init_db as initializer
from app.menus import menu_loop


def main():
    initializer.init_db()
    db = DBController()
    auth = AuthService(db)
    permissions = PermissionManager("./vars/dev/permissions.json")

    try: 
        menu_loop(auth, db, permissions)
    finally:
        auth.close()
        db.close()
if __name__ == "__main__":
    main()
