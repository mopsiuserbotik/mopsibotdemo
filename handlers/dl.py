import asyncio
from telethon import events

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.dl$"))
    async def delete_all_messages(event):
        try:
            me = await client.get_me()
            async for msg in client.iter_messages(event.chat_id, reverse=True):
                if msg.sender_id == me.id:
                    try:
                        await msg.delete()
                        await asyncio.sleep(0.05)
                    except:
                        pass
            await event.delete()
        except Exception as e:
            print(f"[DL] Ошибка: {e}")