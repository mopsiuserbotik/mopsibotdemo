from telethon import events
import asyncio
import os
import re

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.(speedup|slowed)(.*)"))
    async def speed_control(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("**ответь на аудио, голосовое или видео**")
            return

        args = event.pattern_match.group(2).strip().split()
        mode = event.pattern_match.group(1)

        try:
            speed = 1.35 if mode == "speedup" else 0.85
            reverb = False

            for arg in args:
                if re.match(r"^\d+(\.\d+)?$", arg):
                    speed = float(arg)
                elif arg.lower() == "reverb":
                    reverb = True

            effect = "aecho=0.8:0.88:6:0.4," if reverb else ""
            await event.respond(f"**{mode} x{speed} {'с ревербом' if reverb else ''}...**")

            input_path = await client.download_media(reply.media)

            ext = "mp3"
            if reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith("video")):
                ext = "mp4"
            elif reply.voice or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith("audio")):
                ext = "mp3"

            base = os.path.splitext(os.path.basename(input_path))[0]
            safe_base = re.sub(r'[^a-zA-Z0-9]', '_', base)
            output_path = f"/data/data/com.termux/files/home/{safe_base}_{mode}.{ext}"

            if ext == "mp3":
                ffmpeg_filter = f"{effect}atempo={speed}"
                codec = ["-c:a", "libmp3lame", "-b:a", "256k"]
            else:
                ffmpeg_filter = f"[0:v]setpts={1/speed}*PTS[v];[0:a]{effect}atempo={speed}[a]"
                codec = ["-map", "[v]", "-map", "[a]", "-preset", "fast"]

            process_args = [
                "ffmpeg", "-y", "-i", input_path
            ]

            if ext == "mp3":
                process_args += ["-af", ffmpeg_filter] + codec + [output_path]
            else:
                process_args += [
                    "-filter_complex", ffmpeg_filter
                ] + codec + [output_path]

            process = await asyncio.create_subprocess_exec(
                *process_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()

            if not os.path.isfile(output_path):
                await event.respond(f"**ffmpeg не создал файл**\n```{stderr.decode().strip()}```")
                return

            await client.send_file(event.chat_id, output_path, caption=f"**{mode} x{speed} {'(reverb)' if reverb else ''}**")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка: {e}**")

        finally:
            for f in [input_path, output_path]:
                if f and os.path.exists(f):
                    os.remove(f)