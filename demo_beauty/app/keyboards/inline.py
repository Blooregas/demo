from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.models import Service
from app.database.models import Appointment

def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💅 Записаться на сеанс", callback_data="booking_start"))
    builder.row(
        InlineKeyboardButton(text="👤 Мои записи", callback_data="profile_appointments"),
        InlineKeyboardButton(text="💬 Спросить ИИ-мастера", callback_data="ai_consult")
    )
    builder.row(InlineKeyboardButton(text="📍 Контакты и прайс", callback_data="info_contacts"))
    return builder.as_markup()

def services_kb(services: list[Service]) -> InlineKeyboardMarkup:
    """Генерирует кнопки с услугами из базы данных"""
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.row(InlineKeyboardButton(
            text=f"{service.name} — {service.price} ₽",
            callback_data=f"service_{service.id}"
        ))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()

def dates_kb() -> InlineKeyboardMarkup:
    """Генерирует ленту ближайших 7 дней"""
    builder = InlineKeyboardBuilder()
    today = datetime.now()
    days_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    
    for i in range(7):
        date_obj = today + timedelta(days=i)
        day_name = days_ru[date_obj.weekday()]
        date_str = date_obj.strftime("%d.%m")
        db_date_format = date_obj.strftime("%Y-%m-%d")
        builder.button(text=f"{date_str} ({day_name})", callback_data=f"date_{db_date_format}")
    
    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="booking_start"))
    return builder.as_markup()

def times_kb(available_slots: list[str]) -> InlineKeyboardMarkup:
    """Генерирует кнопки со свободным временем"""
    builder = InlineKeyboardBuilder()
    if not available_slots:
        builder.row(InlineKeyboardButton(text="Нет свободных мест 😔", callback_data="dummy"))
    else:
        for slot in available_slots:
            builder.button(text=slot, callback_data=f"time_{slot}")
        builder.adjust(4)
        
    builder.row(InlineKeyboardButton(text="🔙 Назад к датам", callback_data="back_to_dates"))
    return builder.as_markup()
def profile_kb(appointments: list[Appointment]) -> InlineKeyboardMarkup:
    """Генерирует кнопки для управления записями в профиле"""
    builder = InlineKeyboardBuilder()
    
    if appointments:
        for appt in appointments:
            # Создаем кнопку отмены с ID конкретной записи
            builder.row(InlineKeyboardButton(
                text=f"❌ Отменить запись на {appt.start_time.strftime('%d.%m %H:%M')}",
                callback_data=f"cancel_{appt.id}"
            ))
            
    builder.row(InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main"))
    return builder.as_markup()