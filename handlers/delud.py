import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r'\.del (up|down)'))
    async def del_range(event):
        if not event.is_reply:
            return await event.reply("**ответь на сообщение, откуда удалять**")

        reply_msg = await event.get_reply_message()
        if reply_msg is None:
            return await event.reply("**ответь на сообщение, откуда удалять**")

        if hasattr(reply_msg, '__iter__') and not isinstance(reply_msg, (str, bytes)):
            reply_msg = reply_msg[0]

        direction = event.pattern_match.group(1)
        chat = await event.get_chat()
        me = await client.get_me()

        is_pm = event.is_private
        is_admin = False

        if not is_pm:
            try:
                perms = await client.get_permissions(chat.id, me.id)
                is_admin = perms.is_admin and perms.delete_messages
            except:
                pass
            if not is_admin:
                return await event.reply("**нет прав админа**")

        reverse = direction == "down"
        collected = []

        async for msg in client.iter_messages(event.chat_id, reverse=reverse, offset_id=reply_msg.id):
            if direction == "up" and msg.id >= reply_msg.id:
                continue
            if direction == "down" and msg.id <= reply_msg.id:
                continue
            collected.append(msg.id)

            if len(collected) >= 100:
                try:
                    await client.delete_messages(event.chat_id, collected)
                except:
                    pass
                collected.clear()
                await asyncio.sleep(0.3)

        if collected:
            try:
                await client.delete_messages(event.chat_id, collected)
            except:
                pass

        await event.delete()