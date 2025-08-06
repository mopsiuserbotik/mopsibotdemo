import os
import re
import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.audio$"))
    async def extract_audio(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("**ответь на видео, аудио или кружок**")
            return

        await event.respond("**извлекаю аудио...**")

        try:
            input_path = await client.download_media(reply.media)
            base = os.path.splitext(os.path.basename(input_path))[0]
            safe_base = re.sub(r'[^a-zA-Z0-9]', '_', base)
            output_path = f"/data/data/com.termux/files/home/audio.m4a"

            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", input_path,
                "-vn", "-acodec", "copy",
                output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()

            if not os.path.isfile(output_path):
                await event.respond(f"**ffmpeg не создал аудиофайл**\n```{stderr.decode().strip()}```")
                return

            await client.send_file(event.chat_id, output_path, caption="**аудио извлечено без потерь**")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка: {e}**")

        finally:
            for f in [input_path, output_path]:
                if f and os.path.exists(f):
                    os.remove(f)