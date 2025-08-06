import os
import asyncio
from telethon import events
from telethon.errors import FloodWaitError

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.spam (\d+)(?: (.+))?"))
    async def spam_handler(event):
        count = int(event.pattern_match.group(1))
        msg_text = event.pattern_match.group(2)
        reply = await event.get_reply_message()

        if count < 1:
            await event.respond("**число сообщений должно быть больше 0**")
            return

        count = min(count, 100)

        try:
            if msg_text:
                for _ in range(count):
                    try:
                        await event.respond(msg_text)
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds + 1)

            elif reply:
                media = await reply.download_media() if reply.media else None
                for _ in range(count):
                    try:
                        await client.send_message(
                            entity=event.chat_id,
                            message=reply.message or None,
                            file=media,
                            buttons=getattr(reply, "buttons", None),
                            link_preview=getattr(reply, "link_preview", None),
                            parse_mode=None
                        )
                    except FloodWaitError as e:
                        await asyncio.sleep(e.seconds + 1)

                if media and os.path.exists(media):
                    try:
                        os.remove(media)
                    except:
                        pass

            else:
                await event.respond("**укажи текст или ответь на сообщение**")
                return

        except Exception as e:
            await event.respond(f"**ошибка:** `{e}`")
            return

        try:
            await event.delete()
        except:
            pass