import logging
from openai import AsyncOpenAI
from app.core.config import config

# Инициализируем асинхронного клиента
# Если ключа нет в .env, ИИ просто не будет работать, но бот не упадет
client = AsyncOpenAI(
    api_key=config.llm_api_key,
    base_url="https://openrouter.ai/api/v1" # Добавляем этот URL
) if config.llm_api_key else None

# Системный промпт (Инструкция для нейросети)
SYSTEM_PROMPT = """
Ты — профессиональный, вежливый и креативный ИИ-ассистент студии маникюра "Nail Art".
Твоя задача: консультировать клиентов по вопросам маникюра, педикюра, ухода за ногтями и дизайна.
Тон: дружелюбный, экспертный, используй эмодзи, но не перебарщивай.

Прайс-лист (для справки):
- Снятие + Маникюр + Покрытие (однотон) = 2000 ₽ (2 часа)
- Педикюр с покрытием = 2500 ₽ (2 часа)
- Френч / Дизайн = +500 ₽ (доп. 30 мин)

Правила:
1. Отвечай кратко, емко и по делу (в формате Telegram-сообщения, не более 1000 символов).
2. Никогда не придумывай цены, которых нет в прайсе.
3. В конце консультации ненавязчиво предложи записаться на сеанс (через главное меню).
4. Если вопрос не касается ногтей, красоты или студии — вежливо откажись отвечать.
"""

async def ask_ai_consultant(user_question: str) -> str:
    """Отправляет запрос в LLM и возвращает ответ"""
    if not client:
        return "⚠️ Извините, ИИ-консультант временно недоступен (API ключ не настроен)."

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini", # Или "gemini-1.5-flash", если используешь Vertex/Gemini SDK
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question}
            ],
            temperature=0.7, # Чуть-чуть креативности для дизайна
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка LLM API: {e}")
        return "Ой! Мой нейронный мозг немного завис. Попробуйте спросить чуть позже 💅"