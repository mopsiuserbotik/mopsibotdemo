from telethon import events, functions, types

auto_react_chats = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ar(?: (\S+))? (on|off)$"))
    async def toggle_autoreact(event):
        chat_id = event.chat_id
        emoji = event.pattern_match.group(1)
        mode = event.pattern_match.group(2)

        if mode == "off":
            auto_react_chats.pop(chat_id, None)
        elif mode == "on":
            if not emoji:
                await event.respond("**Укажи эмодзи**: `.ar 👍 on`")
                return
            auto_react_chats[chat_id] = emoji

        await event.delete()

    @client.on(events.NewMessage())
    async def react_new_message(event):
        chat_id = event.chat_id
        emoji = auto_react_chats.get(chat_id)
        if not emoji or event.out or (event.is_channel and not event.is_group):
            return
        try:
            await client(functions.messages.SendReactionRequest(
                peer=chat_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=emoji)]
            ))
        except:
            pass