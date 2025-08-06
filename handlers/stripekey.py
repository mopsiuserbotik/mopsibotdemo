import aiohttp
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.stripekey\s+(sk_\w{20,})"))
    async def check_stripe_key(event):
        key = event.pattern_match.group(1)
        headers = {
            "Authorization": f"Bearer {key}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.stripe.com/v1/account", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        name = data.get("display_name", "не указано")
                        await event.reply(f"**Ключ действителен**\nИмя: `{name}`")
                    elif resp.status == 401:
                        await event.reply("**Ключ недействителен (401 Unauthorized)**")
                    else:
                        await event.reply(f"**Ошибка проверки: HTTP {resp.status}**")

        except Exception as e:
            await event.reply(f"**ошибка при запросе:** `{str(e)}`")