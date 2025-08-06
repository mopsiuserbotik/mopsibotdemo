import os
import json
import time
from telethon import events

timer_data_path = "timer_data.json"
timers = {}

def load_timers():
    global timers
    if os.path.exists(timer_data_path):
        try:
            with open(timer_data_path, "r", encoding="utf-8") as f:
                timers.update(json.load(f))
        except Exception:
            timers.clear()

def save_timers():
    try:
        with open(timer_data_path, "w", encoding="utf-8") as f:
            json.dump(timers, f)
    except Exception:
        pass

def format_duration(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    parts = []
    if days: parts.append(f"{days} д.")
    if hours: parts.append(f"{hours} ч.")
    if minutes: parts.append(f"{minutes} мин.")
    if secs or not parts: parts.append(f"{secs} сек.")
    return " ".join(parts)

def register(client):
    load_timers()

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sks$"))
    async def start_or_show_timer(event):
        global timers
        user_id = str(event.sender_id)
        now = int(time.time())

        t = timers.get(user_id)
        if not t or not t.get("running"):
            timers[user_id] = {
                "start": now,
                "elapsed": t.get("elapsed", 0) if t else 0,
                "running": True
            }
            save_timers()
            await event.respond("**счётчик запущен**")
        else:
            total = t.get("elapsed", 0) + (now - t["start"])
            await event.respond(f"**с момента запуска прошло:** {format_duration(total)}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.scp$"))
    async def pause_timer(event):
        global timers
        user_id = str(event.sender_id)
        now = int(time.time())
        t = timers.get(user_id)

        if t and t.get("running"):
            elapsed = t.get("elapsed", 0) + (now - t["start"])
            timers[user_id] = {
                "elapsed": elapsed,
                "running": False
            }
            save_timers()
            await event.respond("**счётчик приостановлен**")
        elif t:
            await event.respond("**счётчик уже на паузе**")
        else:
            await event.respond("**нет активного счётчика для паузы**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.skc$"))
    async def clear_timer(event):
        global timers
        user_id = str(event.sender_id)
        if user_id in timers:
            timers.pop(user_id)
            save_timers()
            await event.respond("**счётчик удалён**")
        else:
            await event.respond("**у тебя нет активного счётчика**")