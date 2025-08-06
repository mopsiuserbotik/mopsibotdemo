import asyncio
from datetime import timedelta
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.timer (\d{1,2}):(\d{1,2}):(\d{1,2})"))
    async def timer_handler(event):
        h, m, s = map(int, event.pattern_match.groups())
        total_seconds = h * 3600 + m * 60 + s

        if total_seconds <= 0:
            await event.respond("**укажи положительное время**")
            return

        try:
            message = await event.respond(f"**осталось:** {h:02}:{m:02}:{s:02}")
            for remaining in range(total_seconds - 1, -1, -1):
                await asyncio.sleep(1)
                t = str(timedelta(seconds=remaining))
                t = "0" + t if remaining < 3600 else t
                await message.edit(f"**осталось:** {t}")
            await message.edit("**время вышло!**")
        except Exception as e:
            await event.respond(f"**ошибка таймера:** `{e}`")