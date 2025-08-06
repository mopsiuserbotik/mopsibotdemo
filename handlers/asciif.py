import asyncio
import os
from PIL import Image
from telethon import events

ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, width):
    w, h = image.size
    aspect = h / w
    return image.resize((width, int(width * aspect * 0.55)))

def image_to_ascii(path, max_length=4096):
    image = Image.open(path).convert("L")
    width = 80
    while width > 10:
        img = resize_image(image, width)
        pixels = img.getdata()
        chars = "".join(ASCII_CHARS[p * len(ASCII_CHARS) // 256] for p in pixels)
        ascii_img = "\n".join(chars[i:i + img.width] for i in range(0, len(chars), img.width))
        if len(ascii_img) <= max_length:
            return ascii_img
        width -= 5
    return "**не удалось уместить изображение в лимит**"

def register(client):
    @client.on(events.NewMessage(pattern=r"\.asciif", outgoing=True))
    async def asciif_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.photo:
            await event.respond("**ответь на фото**")
            return

        path = await reply.download_media()
        try:
            ascii_art = image_to_ascii(path)
            await event.respond(f"```\n{ascii_art}\n```" if not ascii_art.startswith("**") else ascii_art)
        except Exception as e:
            await event.respond(f"**ошибка:** {e}")
        finally:
            if os.path.exists(path):
                os.remove(path)