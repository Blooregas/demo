from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import User, Service, Appointment
from app.states.booking import BookingFSM
from app.keyboards.inline import main_menu_kb, services_kb, dates_kb, times_kb
from app.services.time_slots import get_available_slots

router = Router()

# --- СТАРТ И РЕГИСТРАЦИЯ ---
@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    user_id = message.from_user.id
    
    stmt = select(User).where(User.telegram_id == user_id)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=user_id,
            full_name=message.from_user.full_name,
            username=message.from_user.username
        )
        session.add(user)
        await session.commit()

    await message.answer(
        f"Добро пожаловать в студию маникюра <b>Nail Art</b>, {message.from_user.full_name}! ✨\n\n"
        f"Выберите нужное действие ниже:",
        reply_markup=main_menu_kb()
    )

# --- ВОЗВРАТ В ГЛАВНОЕ МЕНЮ ---
@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await callback.answer()

# --- ШАГ 1: Начало записи ---
@router.callback_query(F.data == "booking_start")
async def process_booking_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    services = (await session.scalars(select(Service))).all()
    if not services:
        await callback.answer("Услуги пока не добавлены админом.", show_alert=True)
        return

    await state.set_state(BookingFSM.choosing_service)
    await callback.message.edit_text("💅 <b>Выберите услугу:</b>", reply_markup=services_kb(services))
    await callback.answer()

# --- ШАГ 2: Выбор услуги ---
@router.callback_query(BookingFSM.choosing_service, F.data.startswith("service_"))
async def process_service_selection(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)
    
    await state.set_state(BookingFSM.choosing_date)
    await callback.message.edit_text("📅 <b>Выберите удобный день:</b>", reply_markup=dates_kb())
    await callback.answer()

# --- Возврат к датам (кнопка "Назад к датам") ---
@router.callback_query(BookingFSM.choosing_time, F.data == "back_to_dates")
async def back_to_dates_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BookingFSM.choosing_date)
    await callback.message.edit_text("📅 <b>Выберите удобный день:</b>", reply_markup=dates_kb())
    await callback.answer()

# --- ШАГ 3: Выбор даты и генерация слотов ---
@router.callback_query(BookingFSM.choosing_date, F.data.startswith("date_"))
async def process_date_selection(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    selected_date_str = callback.data.split("_")[1]
    await state.update_data(date=selected_date_str)
    
    user_data = await state.get_data()
    service = await session.get(Service, user_data["service_id"])
    target_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    
    # Расчет свободного времени
    available_slots = await get_available_slots(session, target_date, service.duration_minutes)
    
    await state.set_state(BookingFSM.choosing_time)
    await callback.message.edit_text(
        f"🕒 <b>Свободное время на {selected_date_str}:</b>\n"
        f"<i>Услуга занимает {service.duration_minutes} мин.</i>",
        reply_markup=times_kb(available_slots)
    )
    await callback.answer()

# --- ШАГ 4: Выбор времени и сохранение ---
@router.callback_query(BookingFSM.choosing_time, F.data.startswith("time_"))
async def process_time_selection(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    selected_time = callback.data.split("_")[1]
    user_data = await state.get_data()
    
    start_time = datetime.strptime(f"{user_data['date']} {selected_time}", "%Y-%m-%d %H:%M")
    service = await session.get(Service, user_data["service_id"])
    end_time = start_time + timedelta(minutes=service.duration_minutes)
    
    # Сохраняем в БД
    new_appointment = Appointment(
        user_id=callback.from_user.id,
        service_id=service.id,
        start_time=start_time,
        end_time=end_time
    )
    session.add(new_appointment)
    await session.commit()
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ <b>Вы успешно записаны!</b>\n\n"
        f"💅 Услуга: {service.name}\n"
        f"📅 Дата: {user_data['date']}\n"
        f"🕒 Время: {selected_time}\n\n"
        f"<i>Ждем вас в нашей студии!</i>"
    )
    await callback.message.answer("Главное меню:", reply_markup=main_menu_kb())
    await callback.answer()