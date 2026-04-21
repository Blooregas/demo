from aiogram.fsm.state import State, StatesGroup

class AIChatFSM(StatesGroup):
    chatting = State() # Клиент находится в режиме диалога с ИИ