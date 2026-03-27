import time
import os
import redis.asyncio as redis
from fastapi import Request, HTTPException

# Підключаємось до Redis (назва хоста 'redis' береться з docker-compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
r = redis.from_url(REDIS_URL, decode_responses=True)

# Задаємо ліміти: (кількість_запитів, вікно_в_секундах)
RATE_LIMITS = {
    "anonymous": (2, 60),       
    "authenticated": (10, 60),  
}

async def rate_limit(request: Request, user_id: str | None = None):
    """
    Алгоритм Sliding Time Window для обмеження запитів.
    """
    # Визначаємо, хто до нас прийшов: юзер з токеном чи просто IP-адреса
    identity = user_id if user_id else request.client.host
    limit_type = "authenticated" if user_id else "anonymous"
    
    # Дістаємо відповідні ліміти
    limit, period = RATE_LIMITS[limit_type]

    # Формуємо унікальний ключ для Redis
    key = f"rate_limit:{identity}"
    
    # Працюємо з часом
    now = time.time()  # Беремо точний час як float, щоб уникнути колізій
    window_start = now - period

    # 1. Очищаємо всі старі записи, які вже вийшли за межі нашої 1 хвилини
    await r.zremrangebyscore(key, min=0, max=window_start)
    
    # 2. Рахуємо, скільки запитів залишилося в поточному вікні
    request_count = await r.zcard(key)
    
    # 3. Перевіряємо, чи не перевищено ліміт
    if request_count >= limit:
        raise HTTPException(status_code=429, detail="Too many requests")
        
    # 4. Якщо все ок — записуємо цей поточний запит у Redis
    # Використовуємо now як score для сортування, і str(now) як унікальне значення
    await r.zadd(key, {str(now): now})
    
    # 5. Оновлюємо час життя ключа (TTL), щоб Redis сам його видалив через хвилину
    await r.expire(key, period)