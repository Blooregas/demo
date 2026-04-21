import enum
from datetime import datetime
from sqlalchemy import String, BigInteger, ForeignKey, Numeric, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass

# --- Enums (Перечисления) ---
class AppointmentStatus(enum.Enum):
    PENDING = "Ожидает подтверждения"
    CONFIRMED = "Подтверждена"
    COMPLETED = "Выполнена"
    CANCELLED = "Отменена"

# --- Модели ---
class User(Base):
    __tablename__ = "users"

    # Используем BigInteger для Telegram ID, так как обычный Integer может переполниться
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Связь с записями (один-ко-многим)
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    specialization: Mapped[str] = mapped_column(String(100)) # Например: "Топ-мастер", "Подолог"
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=5.0)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="master")

class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column() # Храним в целых числах (рубли/центы)
    duration_minutes: Mapped[int] = mapped_column() # Важно для расчета свободных слотов

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Внешние ключи
    user_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id", ondelete="CASCADE"))
    master_id: Mapped[int] = mapped_column(ForeignKey("masters.id", ondelete="SET NULL"), nullable=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"))

    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime) # Вычисляется как start_time + duration_minutes
    
    status: Mapped[AppointmentStatus] = mapped_column(default=AppointmentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="appointments")
    master: Mapped["Master"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")