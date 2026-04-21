from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from app.states.llm import AIChatFSM
from app.services.llm_consultant import ask_ai_consultant
from app.keyboards.inline import main_menu_kb

router = Router()

# Кнопка для выхода из режима диалога
def exit_chat_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Завершить диалог с ИИ")]],
        resize_keyboard=True
    )

# --- Вход в режим ИИ ---
@router.callback_query(F.data == "ai_consult")
async def start_ai_chat(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AIChatFSM.chatting)
    
    await callback.message.answer(
        "✨ <b>ИИ-мастер на связи!</b>\n\n"
        "Задайте мне любой вопрос про маникюр, тренды сезона или уход за кутикулой.\n"
        "<i>(Напишите ваш вопрос в чат)</i>",
        reply_markup=exit_chat_kb()
    )
    await callback.answer()

# --- Выход из режима ИИ ---
@router.message(F.text == "❌ Завершить диалог с ИИ")
async def stop_ai_chat(message: Message, state: FSMContext):
    await state.clear()
    
    # Убираем Reply-клавиатуру и возвращаем Inline главное меню
    from aiogram.types import ReplyKeyboardRemove
    msg = await message.answer("Диалог завершен.", reply_markup=ReplyKeyboardRemove())
    
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

# --- Общение с ИИ (перехват текста) ---
@router.message(AIChatFSM.chatting, F.text)
async def process_ai_question(message: Message):
    # Ставим "печатную машинку", чтобы клиент видел, что бот "думает"
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Отправляем запрос в LLM
    answer = await ask_ai_consultant(message.text)
    
    # Возвращаем ответ пользователю
    await message.answer(answer)