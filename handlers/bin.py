import aiohttp
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.bin\s+(\d{6,8})"))
    async def check_bin(event):
        bin_code = event.pattern_match.group(1)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://lookup.binlist.net/{bin_code}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        country = data.get("country", {}).get("name", "неизвестно")
                        bank = data.get("bank", {}).get("name", "неизвестно")
                        brand = data.get("scheme", "неизвестно")
                        type_ = data.get("type", "неизвестно")

                        await event.reply(
                            f"**Банк:** {bank}\n"
                            f"**Страна:** {country}\n"
                            f"**Бренд:** {brand.upper()}\n"
                            f"**Тип:** {type_.upper()}"
                        )
                    else:
                        await event.reply("**BIN не найден или ошибка API**")
        except Exception as e:
            await event.reply(f"**ошибка запроса:** `{str(e)}`")