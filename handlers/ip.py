import requests
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.ip(?: (.+))?'))
    async def ip_lookup(event):
        await event.delete()
        ip = event.pattern_match.group(1)

        if not ip and event.is_reply:
            reply = await event.get_reply_message()
            ip = reply.message.strip()

        if not ip:
            await event.respond("**укажи IP или ответь на сообщение**")
            return

        try:
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719&lang=ru").json()

            if r.get("status") != "success":
                await event.respond("**не удалось найти информацию**")
                return

            text = (
                f"**IP:** `{r.get('query')}`\n"
                f"**Город:** {r.get('city')}\n"
                f"**Регион:** {r.get('regionName')} ({r.get('region')})\n"
                f"**Страна:** {r.get('country')} ({r.get('countryCode')})\n"
                f"**Провайдер:** {r.get('isp')}\n"
                f"**Организация:** {r.get('org')}\n"
                f"**AS:** {r.get('as')}\n"
                f"**ZIP:** {r.get('zip')}\n"
                f"**Координаты:** {r.get('lat')}, {r.get('lon')}\n"
                f"**Часовой пояс:** {r.get('timezone')}"
            )

            await event.respond(text)

        except Exception as e:
            await event.respond(f"**ошибка:** {e}")