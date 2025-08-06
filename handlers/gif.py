import os
import asyncio
from telethon import events
from tempfile import NamedTemporaryFile

def register(client):
    client.add_event_handler(handler, events.NewMessage(outgoing=True, pattern=r"\.gif$"))

async def handler(event):
    if not event.is_reply:
        await event.respond("**ответь на видео**")
        return

    reply = await event.get_reply_message()
    if not reply.file or not reply.file.mime_type.startswith("video"):
        await event.respond("**это не видео**")
        return

    try:
        with NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
            input_path = tmp_in.name

        await event.client.download_media(reply.media, file=input_path)

        if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
            await event.respond("**не удалось скачать видеофайл**")
            os.remove(input_path)
            return

        output_path = input_path.replace(".mp4", "_converted.mp4")

        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y",
            "-i", input_path,
            "-c:v", "copy",
            "-an",
            output_path,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.communicate()

        if not os.path.exists(output_path):
            await event.respond("**не удалось создать GIF**")
            os.remove(input_path)
            return

        await event.client.send_file(
            event.chat_id,
            output_path,
            reply_to=event.reply_to_msg_id,
            force_document=False
        )

        await event.delete()

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        await event.respond(f"**ошибка:** {e}")