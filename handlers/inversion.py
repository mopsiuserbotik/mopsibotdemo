import os
import io
import asyncio
import tempfile
from PIL import Image
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.inversion"))
    async def inversion_handler(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("**ответь на фото или видео**")
            return

        mime = reply.file.mime_type or ""

        if mime.startswith("image/") or (reply.photo and not mime.startswith("video/")):
            await handle_image_inversion(event, reply)
        elif mime.startswith("video/"):
            await handle_video_inversion(event, reply)
        else:
            await event.respond("**неподдерживаемый формат**")

async def handle_image_inversion(event, reply):
    path = await reply.download_media()
    img = Image.open(path).convert("RGB")
    pixels = img.load()
    w, h = img.size

    for x in range(w):
        for y in range(h):
            r, g, b = pixels[x, y]
            pixels[x, y] = (255 - r, 255 - g, 255 - b)

    output = io.BytesIO()
    img.save(output, format="PNG")
    output.name = "inverted.png"
    output.seek(0)
    await event.respond("**инвертированое фото**", file=output)

    os.remove(path)

async def handle_video_inversion(event, reply):
    msg = await event.respond("**инвертирую видео...**")
    try:
        input_path = await reply.download_media(file=tempfile.NamedTemporaryFile(delete=False).name)
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "negate", "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "copy", output_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        if os.path.exists(output_path):
            await event.client.send_file(event.chat_id, output_path, reply_to=reply.id)
            os.remove(output_path)
        else:
            await msg.edit("**ошибка при обработке видео**")

        os.remove(input_path)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"**ошибка: {e}**")