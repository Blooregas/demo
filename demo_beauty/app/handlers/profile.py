from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database.models import Appointment, AppointmentStatus
from app.keyboards.inline import profile_kb, main_menu_kb

router = Router()

# --- Просмотр личного кабинета ---
@router.callback_query(F.data == "profile_appointments")
async def view_profile(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id

    # Ищем все активные записи пользователя, сортируем по времени
    stmt = select(Appointment).where(
        Appointment.user_id == user_id,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).options(
        joinedload(Appointment.service) # Подтягиваем название услуги из соседней таблицы
    ).order_by(Appointment.start_time)

    appointments = (await session.scalars(stmt)).all()

    if not appointments:
        await callback.message.edit_text(
            "👤 <b>Ваш профиль</b>\n\n"
            "У вас пока нет активных записей 😔",
            reply_markup=profile_kb([])
        )
        return

    # Если записи есть, формируем красивый список
    text = "👤 <b>Ваши предстоящие визиты:</b>\n\n"
    for appt in appointments:
        text += (
            f"💅 <b>Услуга:</b> {appt.service.name}\n"
            f"📅 <b>Дата:</b> {appt.start_time.strftime('%d.%m.%Y')}\n"
            f"🕒 <b>Время:</b> {appt.start_time.strftime('%H:%M')}\n"
            f"⏳ <b>Статус:</b> {appt.status.value}\n"
            f"──────────────\n"
        )

    await callback.message.edit_text(text, reply_markup=profile_kb(appointments))

# --- Отмена записи ---
@router.callback_query(F.data.startswith("cancel_"))
async def cancel_appointment(callback: CallbackQuery, session: AsyncSession):
    # Извлекаем ID записи из callback_data (например, "cancel_12")
    appt_id = int(callback.data.split("_")[1])

    # Находим запись в БД
    appt = await session.get(Appointment, appt_id)
    
    if appt and appt.user_id == callback.from_user.id: # Проверяем, что клиент отменяет СВОЮ запись
        # Меняем статус в БД
        appt.status = AppointmentStatus.CANCELLED
        await session.commit()
        await callback.answer("Запись успешно отменена ✅", show_alert=True)
    else:
        await callback.answer("Ошибка: Запись не найдена.", show_alert=True)

    # После отмены перезагружаем профиль, чтобы список обновился
    await view_profile(callback, session)