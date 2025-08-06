import os
import io
import asyncio
import tempfile
from PIL import Image
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.bw"))
    async def bw_handler(event):
        await asyncio.sleep(0.15)
        reply = await event.get_reply_message()

        if not reply or not reply.media:
            await event.respond("**ответь на фото или видео**")
            return

        mime = reply.file.mime_type or ""

        if mime.startswith("video/"):
            await process_bw_video(event, reply)
        elif mime.startswith("image/") or reply.photo:
            await process_bw_image(event, reply)
        else:
            await event.respond("**неподдерживаемый формат**")

async def process_bw_video(event, reply):
    msg = await event.respond("**обрабатываю видео в ч/б...**")
    try:
        input_path = await reply.download_media(file=tempfile.NamedTemporaryFile(delete=False).name)
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "hue=s=0", "-c:v", "libx264", "-preset", "ultrafast",
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

async def process_bw_image(event, reply):
    msg = await event.respond("**обрабатываю фото в ч/б...**")
    try:
        path = await reply.download_media()
        img = Image.open(path).convert("L")  # grayscale
        output = io.BytesIO()
        img.save(output, format="PNG")
        output.name = "bw.png"
        output.seek(0)
        await event.respond("**готово**", file=output)
        os.remove(path)
        await msg.delete()
    except Exception as e:
        await msg.edit(f"**ошибка: {e}**")