import random
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.random (\-?\d+) (\-?\d+)$'))
    async def random_number(event):
        try:
            a = int(event.pattern_match.group(1))
            b = int(event.pattern_match.group(2))
            if a > b:
                a, b = b, a
            await event.respond(f"**случайное число:** `{random.randint(a, b)}`")
        except Exception:
            await event.respond("**ошибка: укажи два целых числа, например** `.random -10 100`")