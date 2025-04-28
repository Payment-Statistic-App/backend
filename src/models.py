import datetime
import uuid

from enum import Enum
from typing import Dict, Any, Optional, List
from sqlalchemy import UUID, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Roles(Enum):
    student = "student"
    observer = "observer"
    accountant = "accountant"
    admin = "admin"


class OperationTypes(Enum):
    user = "user"
    group = "group"
    semester = "semester"
    payment = "payment"


class Semester(Base):
    __tablename__ = "semesters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }


class Operation(Base):
    __tablename__ = "operations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[OperationTypes] = mapped_column()
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    comment: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="operations", uselist=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "user_id": self.user_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "user": self.user.to_dict()
        }


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    users: Mapped[List["User"]] = relationship(back_populates="group", uselist=True,
                                               lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "users": [user.to_dict() for user in self.users]
        }


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    semester_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("semesters.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column()
    comment: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    user: Mapped["User"] = relationship(back_populates="transactions", uselist=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "semester_id": self.semester_id,
            "amount": self.amount,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()
    role: Mapped[Roles] = mapped_column(default=Roles.student)
    patronymic: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    login: Mapped[str] = mapped_column(unique=True)
    group_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("groups.id"), nullable=True, default=None)
    password_hash: Mapped[bytes] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(default=func.now())

    group: Mapped["Group"] = relationship(back_populates="users", uselist=False)
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="user", uselist=True,
                                                             lazy="selectin", cascade="all, delete-orphan")
    operations: Mapped[List["Operation"]] = relationship(back_populates="user", uselist=True,
                                                           lazy="selectin", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "patronymic": self.patronymic,
            "group_id": self.group_id,
            "phone": self.phone,
            "role": self.role,
            "login": self.login,
            "created_at": self.created_at.isoformat(),
            "transactions": [transaction.to_dict() for transaction in self.transactions],
            "operations": [operation.to_dict() for operation in self.operations]
        }
