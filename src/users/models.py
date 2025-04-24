import datetime
import uuid

from enum import Enum
from typing import Dict, Any
from sqlalchemy import UUID, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Roles(Enum):
    student = "student"
    observer = "observer"
    accountant = "accountant"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()
    role: Mapped[Roles] = mapped_column(default=Roles.student)
    patronymic: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    login: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "surname": self.surname,
            "patronymic": self.patronymic,
            "phone": self.phone,
            "role": self.role,
            "login": self.login,
            "created_at": self.created_at.isoformat(),
        }
