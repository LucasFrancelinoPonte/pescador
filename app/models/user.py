from __future__ import annotations

from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, email: str, password: str, name: str, perfil: str) -> None:
        normalized_email = email.strip().lower()
        self.id = normalized_email
        self.email = normalized_email
        self.password = password
        self.name = name.strip()
        self.perfil = perfil.strip()

    def check_password(self, password: str) -> bool:
        return self.password == password

    def __repr__(self) -> str:
        return f"User(email={self.email!r}, perfil={self.perfil!r})"