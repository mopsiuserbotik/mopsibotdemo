import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.delete (\d+)$"))
    async def clean_handler(event):
        await event.delete()
        try:
            count = int(event.pattern_match.group(1))
            me = (await client.get_me()).id
            deleted = 0

            async for msg in client.iter_messages(event.chat_id, from_user=me):
                if deleted >= count:
                    break
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.1)
                except:
                    continue
        except Exception as e:
            await event.respond(f"**ошибка:** `{e}`")