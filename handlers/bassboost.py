import os
import re
import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.bassboost(?: (\d+))?(?: (\w+))?$"))
    async def bassboost(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("**ответь на аудио, голосовое или видео**")
            return

        boost = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 15
        mode = (event.pattern_match.group(2) or "default").lower()

        if mode not in ["default", "vocal", "nightcore"]:
            await event.respond("**режим недоступен. выбери: default, vocal или nightcore**")
            return

        await event.respond(f"**бас +{boost} дБ, режим: {mode}**")

        try:
            input_path = await client.download_media(reply.media)
            base = os.path.splitext(os.path.basename(input_path))[0]
            safe_base = re.sub(r'[^a-zA-Z0-9]', '_', base)
            output_path = f"/data/data/com.termux/files/home/{safe_base}_bass.mp3"

            if mode == "vocal":
                filter_chain = f"bass=g={int(boost*0.3)},equalizer=f=1500:t=q:w=1:g=6,acompressor=threshold=-16dB:ratio=2:attack=5:release=70,alimiter=limit=0.98"
            elif mode == "nightcore":
                filter_chain = f"atempo=1.25,bass=g={int(boost*0.7)},alimiter=limit=0.98"
            else:  
                filter_chain = f"bass=g={boost},equalizer=f=1000:t=q:w=1:g=5,acompressor=threshold=-18dB:ratio=3:attack=10:release=100,alimiter=limit=0.98"

            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", input_path,
                "-af", filter_chain,
                "-c:a", "libmp3lame", "-b:a", "256k",
                output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()

            if not os.path.isfile(output_path):
                await event.respond(f"**ffmpeg не создал файл**\n```{stderr.decode().strip()}```")
                return

            await client.send_file(event.chat_id, output_path, caption=f"**готово: +{boost} дБ ({mode})**")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка: {e}**")

        finally:
            for f in [input_path, output_path]:
                if f and os.path.exists(f):
                    os.remove(f)