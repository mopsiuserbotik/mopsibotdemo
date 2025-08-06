import asyncio
from telethon import events

k_config = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.k (-?\d+) (.+?) (\d+) (on|off)$"))
    async def handler_k_toggle(event):
        await event.delete()
        group_id = int(event.pattern_match.group(1))
        text = event.pattern_match.group(2)
        count = int(event.pattern_match.group(3))
        state = event.pattern_match.group(4)

        if state == "on":
            k_config[group_id] = {"text": text, "count": count, "enabled": True}
            print(f"**[✓] Включено для {group_id}:** «{text}» ×{count}")
        else:
            if group_id in k_config:
                k_config[group_id]["enabled"] = False
                print(f"**[×] Выключено для {group_id}**")
            else:
                print(f"**[!] Не было активной слежки для {group_id}**")

    @client.on(events.NewMessage())
    async def handler_k_autocomment(event):
        await asyncio.sleep(0.15)
        group_id = event.chat_id
        config = k_config.get(group_id)

        if not config or not config["enabled"]:
            return

        if not (event.post or event.fwd_from or getattr(event.sender_id, "channel_id", None)):
            return

        for i in range(config["count"]):
            try:
                await client.send_message(
                    entity=group_id,
                    message=config["text"],
                    reply_to=event.id
                )
                print(f"**[→] Коммент {i+1}/{config['count']} под {event.id} в {group_id}**")
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"**[×] Ошибка в {group_id}: {e}**")
                break