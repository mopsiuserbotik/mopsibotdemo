from telethon import events

AUTO_DELETE_GLOBAL = False
AUTO_DELETE_CHATS = {}
LAST_MESSAGES = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.autodel(?:\s+(all))?\s+(on|off)$"))
    async def autodel_toggle(event):
        global AUTO_DELETE_GLOBAL, AUTO_DELETE_CHATS
        is_all, state = event.pattern_match.groups()
        chat_id = event.chat_id
        enabled = state == "on"

        if is_all:
            AUTO_DELETE_GLOBAL = enabled
            await event.respond(f"**глобальное автоудаление {'включено' if enabled else 'выключено'}**")
        else:
            AUTO_DELETE_CHATS[chat_id] = enabled
            await event.respond(f"**автоудаление {'включено' if enabled else 'выключено'} в этом чате**")

    @client.on(events.NewMessage(outgoing=True))
    async def autodel_handler(event):
        global AUTO_DELETE_GLOBAL, AUTO_DELETE_CHATS, LAST_MESSAGES
        chat_id = event.chat_id

        if AUTO_DELETE_GLOBAL or AUTO_DELETE_CHATS.get(chat_id):
            last_msg_id = LAST_MESSAGES.get(chat_id)
            if last_msg_id and last_msg_id != event.id:
                try:
                    await client.delete_messages(chat_id, last_msg_id)
                except:
                    pass
            LAST_MESSAGES[chat_id] = event.id