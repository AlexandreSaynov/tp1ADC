from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from schema import User
import hashlib

DB_URL = "sqlite:///app.db"
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)

def hash_password(password: str) -> str:
    """Gera hash SHA256 simples (não recomendado em produção)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class AuthService:
    def __init__(self):
        self.session = Session()

    def register_user(self, username: str, email: str, password: str, access_level: str = "user") -> bool:
        first_user = self.session.query(User).first()

        if not first_user:
            access_level = "admin"
            print("Primeiro utilizador criado como RootAdmin.")

        if self.session.query(User).filter_by(username=username).first():
            print("Nome de utilizador já existente.")
            return False
        if self.session.query(User).filter_by(email=email).first():
            print("Email já existente.")
            return False

        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            access_level=access_level,
            created_at=datetime.now()
        )

        self.session.add(new_user)
        self.session.commit()
        print(f"Utilizador '{username}' criado com sucesso (Role: {access_level}).")
        return True

    def login(self, username: str, password: str):
        user = self.session.query(User).filter_by(username=username).first()

        if not user:
            print("Utilizador não encontrado.")
            return None

        if user.password_hash != hash_password(password):
            print("Palavra-passe incorreta.")
            return None

        print(f"Login efetuado com sucesso. Bem-vindo, {user.username} ({user.access_level})!")
        return user


    def close(self):
        self.session.close()
