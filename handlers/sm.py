from telethon import events

send_to_saved_chats = set()

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.sm (on|off)$"))
    async def toggle_send_to_saved(event):
        global send_to_saved_chats

        chat_id = event.chat_id
        state = event.pattern_match.group(1)

        if state == "on":
            send_to_saved_chats.add(chat_id)
        else:
            send_to_saved_chats.discard(chat_id)

        await event.delete()

    @client.on(events.NewMessage(incoming=True))
    async def forward_content_to_saved(event):
        if event.chat_id not in send_to_saved_chats or event.out:
            return

        try:
            await event.forward_to("me")
        except Exception as e:
            print(f"[sm] Ошибка пересылки: {e}")