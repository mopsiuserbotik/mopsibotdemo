import os
import asyncio
from PIL import Image
from telethon import events

def register(client):
    client.add_event_handler(stick_handler, events.NewMessage(outgoing=True, pattern=r"\.stick$"))

async def stick_handler(event):
    await asyncio.sleep(0.15)
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.respond("**ответь на фото**")
        return

    input_path = await reply.download_media()
    if not input_path:
        await event.respond("**не удалось скачать**")
        return

    try:
        if input_path.lower().endswith((".jpg", ".jpeg", ".png")):
            img = Image.open(input_path).convert("RGBA")
            img.thumbnail((512, 512))
            img.save("st.webp", "WEBP")
            await event.client.send_file(event.chat_id, "st.webp", force_document=False, reply_to=reply.id)
            os.remove("st.webp")
        else:
            await event.respond("**только фото поддерживается**")

    except Exception as e:
        await event.respond(f"**ошибка:** {e}")

    finally:
        if os.path.exists(input_path):
            os.remove(input_path)