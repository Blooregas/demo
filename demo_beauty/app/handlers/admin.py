from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.filters.admin import IsAdmin
from app.states.admin import AddServiceFSM
from app.database.models import Service

# Обрати внимание: мы сразу вешаем фильтр IsAdmin() на весь роутер!
# Теперь ни один обычный клиент не сможет случайно дернуть эти хэндлеры.
router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить услугу", callback_data="admin_add_service"))
    return builder.as_markup()

# --- ВХОД В АДМИНКУ ---
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Здесь вы можете управлять прайс-листом вашей студии.",
        reply_markup=admin_main_kb()
    )

# --- ШАГ 1: Начало добавления услуги ---
@router.callback_query(F.data == "admin_add_service")
async def start_add_service(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddServiceFSM.waiting_for_name)
    await callback.message.edit_text("Введите название новой услуги (например: <i>Снятие + Маникюр</i>):")
    await callback.answer()

# --- ШАГ 2: Ввод названия ---
@router.message(AddServiceFSM.waiting_for_name, F.text)
async def process_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddServiceFSM.waiting_for_price)
    await message.answer("Введите стоимость услуги в рублях (только число, например: <i>2000</i>):")

# --- ШАГ 3: Ввод цены ---
@router.message(AddServiceFSM.waiting_for_price, F.text)
async def process_service_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Пожалуйста, введите только число.")
        return
        
    await state.update_data(price=int(message.text))
    await state.set_state(AddServiceFSM.waiting_for_duration)
    await message.answer("Введите длительность услуги в минутах (например: <i>120</i> для двух часов):")

# --- ШАГ 4: Ввод длительности и сохранение в БД ---
@router.message(AddServiceFSM.waiting_for_duration, F.text)
async def process_service_duration(message: Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer("❌ Пожалуйста, введите только число.")
        return
        
    data = await state.get_data()
    name = data["name"]
    price = data["price"]
    duration = int(message.text)
    
    # Создаем объект услуги и сохраняем в БД
    new_service = Service(
        name=name,
        price=price,
        duration_minutes=duration
    )
    session.add(new_service)
    await session.commit()
    
    await state.clear()
    await message.answer(
        f"✅ <b>Услуга успешно добавлена!</b>\n\n"
        f"💅 Название: {name}\n"
        f"💰 Цена: {price} ₽\n"
        f"⏱ Время: {duration} мин.\n\n"
        f"<i>Теперь клиенты увидят её в меню записи.</i>",
        reply_markup=admin_main_kb()
    )