from aiogram.fsm.state import State, StatesGroup

class BookingFSM(StatesGroup):
    choosing_service = State()  # Шаг 1: Выбор услуги
    choosing_date = State()     # Шаг 2: Выбор дня
    choosing_time = State()     # Шаг 3: Выбор времени сеанса