from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.pin$"))
    async def pin_message(event):
        reply = await event.get_reply_message()
        if not reply:
            return
        try:
            await client.pin_message(event.chat_id, reply.id, notify=False)
            await event.delete()
        except Exception as e:
            await event.reply(f"**ошибка**: {e}")

    @client.on(events.NewMessage(pattern=r"\.unpin$"))
    async def unpin_message(event):
        reply = await event.get_reply_message()
        if not reply:
            return
        try:
            await client.unpin_message(event.chat_id, reply.id)
            await event.delete()
        except Exception as e:
            await event.reply(f"**ошибка**: {e}")