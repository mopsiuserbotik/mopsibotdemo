from telethon import events

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.id$"))
    async def get_id(event):
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            await event.respond(f"**ID:** `{reply.sender_id}`")
        await event.delete()