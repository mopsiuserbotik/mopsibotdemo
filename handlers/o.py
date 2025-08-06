import os
import asyncio
import random
from telethon import events
from telethon.tl.types import (
    DocumentAttributeVideo,
    DocumentAttributeAudio,
    InputMediaUploadedDocument
)
from telethon.tl.functions.messages import SendMediaRequest

def register(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.o (v|g)$"))
    async def convert_ffmpeg(event):
        mode = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not reply or not reply.media:
            await event.respond("**ответь на сообщение с видео или аудио**.")
            return

        try:
            input_path = await client.download_media(reply, file="media_input")
            output = "output.mp4" if mode == "v" else "output.ogg"

            if mode == "v":
                cmd = (
                    f'ffmpeg -y -i "{input_path}" -t 59 '
                    f'-vf "crop=\'min(in_w,in_h)\':\'min(in_w,in_h)\'" '
                    f'-c:v libx264 -preset veryfast -crf 18 -c:a aac -movflags +faststart "{output}"'
                )
                await (await asyncio.create_subprocess_shell(cmd)).communicate()

                file = await client.upload_file(output)
                attributes = [DocumentAttributeVideo(duration=59, w=480, h=480, round_message=True)]
                media = InputMediaUploadedDocument(
                    file=file,
                    mime_type="video/mp4",
                    attributes=attributes
                )

            elif mode == "g":
                cmd = (
                    f'ffmpeg -y -i "{input_path}" -t 59 '
                    f'-vn -acodec libopus -ar 48000 -ac 1 "{output}"'
                )
                await (await asyncio.create_subprocess_shell(cmd)).communicate()

                file = await client.upload_file(output)
                attributes = [DocumentAttributeAudio(duration=59, voice=True)]
                media = InputMediaUploadedDocument(
                    file=file,
                    mime_type="audio/ogg",
                    attributes=attributes
                )

            await client(SendMediaRequest(
                peer=await event.get_input_chat(),
                media=media,
                message="",
                random_id=random.randint(-2**63, 2**63 - 1)
            ))

            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка**: {e}")

        finally:
            for f in ["media_input", "output.mp4", "output.ogg"]:
                if os.path.exists(f):
                    os.remove(f)