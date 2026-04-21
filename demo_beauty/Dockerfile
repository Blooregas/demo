# Используем легковесный официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Настройки Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта
COPY . .

# --- ТОТ САМЫЙ ИНДУСТРИАЛЬНЫЙ СТАНДАРТ ---
# 1. Создаем системного пользователя appuser
# 2. Отдаем ему права на папку /app (включая базу данных sqlite)
RUN useradd -m -r appuser && chown -R appuser:appuser /app

# 3. Переключаем Docker на этого пользователя
USER appuser
# ----------------------------------------

# Запускаем бота
CMD ["python", "run.py"]