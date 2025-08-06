import os
import asyncio
import random
from telethon import events
from telethon.errors import FloodWaitError

loop_spam_tasks = {}

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.sendloop$"))
    async def start_send_loop(event):
        await asyncio.sleep(0.1)
        reply = await event.get_reply_message()
        chat_id = event.chat_id

        if not reply:
            await event.respond("**ответь на сообщение, которое нужно слать**")
            return

        if chat_id in loop_spam_tasks:
            await event.respond("**уже запущено**")
            return

        media_path = await reply.download_media() if reply.media else None
        await event.respond("**бесконечная рассылка запущена**")

        async def spam():
            while True:
                try:
                    await client.send_message(
                        chat_id,
                        message=reply.text or "",
                        file=media_path,
                        buttons=reply.buttons if reply.buttons else None,
                        link_preview=getattr(reply, "link_preview", None)
                    )
                    await asyncio.sleep(random.randint(20, 40))
                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds + 1)
                except Exception:
                    await asyncio.sleep(5)

        task = asyncio.create_task(spam())
        loop_spam_tasks[chat_id] = (task, media_path)

        try:
            await event.delete()
        except:
            pass

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.stopsend$"))
    async def stop_send_loop(event):
        chat_id = event.chat_id
        task_data = loop_spam_tasks.pop(chat_id, None)

        if not task_data:
            await event.respond("**ничего не запущено в этом чате**")
            return

        task, media_path = task_data
        task.cancel()

        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
            except:
                pass

        await event.respond("**бесконечный спам остановлен**")