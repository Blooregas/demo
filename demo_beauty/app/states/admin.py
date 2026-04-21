from aiogram.fsm.state import State, StatesGroup

class AddServiceFSM(StatesGroup):
    waiting_for_name = State()       # Название услуги (строка)
    waiting_for_price = State()      # Цена (число)
    waiting_for_duration = State()   # Длительность в минутах (число)