from telethon import events
import asyncio
import os

def time_to_seconds(t: str) -> int:
    parts = t.split(':')
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
        return 0

def register(client):
    client.add_event_handler(video_trim, events.NewMessage(outgoing=True, pattern=r"\.vrz (\d{1,2}:\d{2}(?::\d{2})?) (\d{1,2}:\d{2}(?::\d{2})?)"))

async def video_trim(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.respond("**ответь на сообщение с видео**")
        return

    start_time = time_to_seconds(event.pattern_match.group(1))
    end_time = time_to_seconds(event.pattern_match.group(2))
    if start_time >= end_time:
        await event.respond("**время начала должно быть меньше времени окончания**")
        return

    await event.respond("**скачиваю видео...**")
    input_path = await event.client.download_media(reply.media, file="temp_input_video")
    if not input_path or not os.path.isfile(input_path):
        await event.respond("**не удалось скачать видео**")
        return

    output_path = "temp_output_video.mp4"
    cmd = [
        "ffmpeg", "-ss", str(start_time), "-i", input_path, "-t",
        str(end_time - start_time), "-c", "copy", "-avoid_negative_ts", "make_zero", "-y", output_path
    ]

    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        await event.respond(f"**ошибка при обрезке видео:**\n{stderr.decode()}")
        os.remove(input_path)
        return

    await event.client.send_file(event.chat_id, output_path, reply_to=reply.id)
    os.remove(input_path)
    os.remove(output_path)
    await event.delete()