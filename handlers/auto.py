import asyncio
from telethon import events

auto_reply_chats = {}
auto_reply_global = None

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.auto(?: all)?(?: .+)?$"))
    async def auto_toggle(event):
        global auto_reply_chats, auto_reply_global

        await event.delete()
        parts = event.raw_text.split(maxsplit=3)

        if len(parts) < 3:
            await event.respond("**пример:** `.auto привет on` или `.auto all я бот off`")
            return

        is_global = parts[1] == "all"

        if is_global:
            if len(parts) < 4:
                await event.respond("**пример:** `.auto all я бот on/off`")
                return
            text = parts[2]
            state = parts[3].lower()
        else:
            text = parts[1]
            state = parts[2].lower()

        if state not in ("on", "off"):
            await event.respond("**последнее должно быть `on` или `off`**")
            return

        if is_global:
            if state == "on":
                auto_reply_global = text
            else:
                auto_reply_global = None
        else:
            chat_id = event.chat_id
            if state == "on":
                auto_reply_chats[chat_id] = text
            else:
                auto_reply_chats.pop(chat_id, None)

    @client.on(events.NewMessage(incoming=True))
    async def auto_reply(event):
        if event.out:
            return

        chat_id = event.chat_id
        text = auto_reply_chats.get(chat_id) or auto_reply_global
        if not text:
            return

        try:
            if event.sender and event.sender.bot:
                return

            me = await client.get_me()
            mention = me.username and f"@{me.username.lower()}" in (event.raw_text or "").lower()
            reply_to_me = event.is_reply and (await event.get_reply_message()).sender_id == me.id

            if event.is_private or mention or reply_to_me:
                await event.reply(text)
        except Exception as e:
            print(f"[auto_reply] ошибка: {e}")