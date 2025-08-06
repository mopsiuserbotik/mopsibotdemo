import random
import requests
from telethon import events

def register(client):
    client.add_event_handler(generate_proxies, events.NewMessage(pattern=r"\.proxy(?:\s*(\d+))?"))

async def generate_proxies(event):
    count = event.pattern_match.group(1)
    try:
        count = max(1, min(int(count), 50)) if count else 1
    except:
        count = 1

    url = "https://www.proxy-list.download/api/v1/get?type=http"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            await event.respond("**не удалось получить список прокси**")
            return

        proxies = [p for p in resp.text.strip().splitlines() if p]
        if not proxies:
            await event.respond("**список прокси пуст**")
            return

        selected = random.sample(proxies, min(count, len(proxies)))
        await event.respond("```\n" + "\n".join(selected) + "\n```")

    except Exception as e:
        await event.respond(f"**ошибка при получении прокси:** {e}")