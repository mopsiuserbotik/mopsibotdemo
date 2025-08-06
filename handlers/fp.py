from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.photos import UploadProfilePhotoRequest
import asyncio
import random
import os

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.fp (\d+)$"))
    async def set_photo_multiple(event):
        await asyncio.sleep(0.1)
        count = int(event.pattern_match.group(1))

        if count < 1 or count > 1000:
            await event.respond("**укажи число от 1 до 1000(в идеале не больше 29)**")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.photo:
            await event.respond("**ответь на фото чтобы поставить на аву**")
            return

        msg = await event.respond("**загружаю фото...**")

        try:
            path = await client.download_media(reply)
            file = await client.upload_file(path)
        except Exception as e:
            await msg.edit(f"**ошибка загрузки:** {e}")
            return

        await msg.edit("**начинаю установку аватарок...**")
        done = 0

        while done < count:
            try:
                await client(UploadProfilePhotoRequest(file=file))
                done += 1
                await msg.edit(f"**установлено: {done} / {count}**")
                await asyncio.sleep(random.uniform(1, 2) if count > 25 else 1.1)

            except FloodWaitError as e:
                await msg.edit(f"**FloodWait: жду {e.seconds} сек...**")
                await asyncio.sleep(e.seconds + 1)
            except Exception as e:
                await msg.edit(f"**ошибка:** {e}")
                break

        await msg.edit("**готово. аватарки установлены**")
        await event.delete()

        try:
            os.remove(path)
        except:
            pass