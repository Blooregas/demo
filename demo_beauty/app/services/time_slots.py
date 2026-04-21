from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database.models import Appointment

# Рабочие часы студии (в идеале их тоже нужно хранить в БД, но для MVP захардкодим)
WORK_START_HOUR = 10
WORK_END_HOUR = 20
SLOT_STEP_MINUTES = 30 # Шаг сетки расписания (каждые 30 минут)

async def get_available_slots(session: AsyncSession, target_date: date, service_duration: int) -> list[str]:
    """
    Генерирует список свободного времени на выбранную дату с учетом уже существующих записей
    и длительности новой услуги.
    """
    # 1. Определяем границы выбранного дня
    day_start = datetime.combine(target_date, time(WORK_START_HOUR, 0))
    day_end = datetime.combine(target_date, time(WORK_END_HOUR, 0))

    # 2. Достаем все записи на этот день из БД
    stmt = select(Appointment).where(
        and_(
            Appointment.start_time >= day_start,
            Appointment.start_time < day_end,
            Appointment.status != "CANCELLED" # Отмененные записи не занимают время
        )
    ).order_by(Appointment.start_time)
    
    existing_appointments = (await session.scalars(stmt)).all()

    available_slots = []
    current_time = day_start
    now = datetime.now()

    # 3. Идем по дню с шагом 30 минут
    while current_time + timedelta(minutes=service_duration) <= day_end:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=service_duration)

        # Если дата - сегодня, отсекаем прошедшее время
        if slot_start <= now:
            current_time += timedelta(minutes=SLOT_STEP_MINUTES)
            continue

        # 4. Проверяем пересечение (Overlap) с существующими записями
        is_overlapping = False
        for appt in existing_appointments:
            # Формула пересечения двух интервалов: (StartA < EndB) and (EndA > StartB)
            if slot_start < appt.end_time and slot_end > appt.start_time:
                is_overlapping = True
                break
        
        if not is_overlapping:
            # Слот свободен, добавляем в список (форматируем как "10:00")
            available_slots.append(slot_start.strftime("%H:%M"))

        current_time += timedelta(minutes=SLOT_STEP_MINUTES)

    return available_slots