from telethon import events
import asyncio

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.clean$"))
    async def clean_all(event):
        await event.delete()
        chat = await event.get_chat()

        offset_id = 0
        limit = 100

        try:
            while True:
                messages = [msg async for msg in client.iter_messages(chat.id, limit=limit, offset_id=offset_id)]
                if not messages:
                    break

                ids = [msg.id for msg in messages]
                offset_id = min(ids)

                try:
                    await client.delete_messages(chat.id, ids)
                except:
                    pass

                await asyncio.sleep(0.25)

        except Exception as e:
            await event.respond(f"**ошибка:** {e}")