from telethon import events
from telethon.errors import FloodWaitError
import asyncio

monitor_enabled = {}
user_ids = {}

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.mnd (on|off)$"))
    async def toggle_monitor_and_delete(event):
        state = event.pattern_match.group(1)
        if client not in user_ids:
            me = await client.get_me()
            user_ids[client] = me.id
        monitor_enabled[user_ids[client]] = (state == "on")
        await event.respond(f"**удаление входящих сообщений** {'включено' if state == 'on' else 'отключено'}")

    @client.on(events.NewMessage(incoming=True))
    async def monitor_and_delete(event):
        user_id = user_ids.get(client)
        if user_id is None:
            me = await client.get_me()
            user_id = me.id
            user_ids[client] = user_id
        if not monitor_enabled.get(user_id, False):
            return
        try:
            if event.sender_id and event.sender_id != user_id:
                await event.delete()
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except:
            pass