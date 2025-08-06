from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sv$"))
    async def save_to_saved(event):
        reply = await event.get_reply_message()
        if not reply:
            return await event.respond("**нужен реплай на сообщение**")

        try:
            await client.forward_messages("me", reply)
        except Exception as e:
            await event.respond(f"**ошибка:** {str(e)[:100]}")
        finally:
            await event.delete()