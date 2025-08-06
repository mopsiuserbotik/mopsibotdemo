import os
import re
import asyncio
import tempfile
import requests
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tiktok(?: (.+))?"))
    async def tiktok_dl(event):
        await asyncio.sleep(0.15)
        url = event.pattern_match.group(1)

        if not url and event.is_reply:
            reply = await event.get_reply_message()
            if reply and reply.raw_text:
                match = re.search(r'https?://[^\s]*tiktok\.com[^\s]*', reply.raw_text)
                if match:
                    url = match.group(0)

        if not url or "tiktok.com" not in url:
            await event.respond("**укажи ссылку на TikTok или ответь на сообщение с ней**")
            return

        msg = await event.respond("**скачиваю...**")

        try:
            api_url = f"https://tikwm.com/api/?url={url}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(api_url, headers=headers, timeout=10).json()

            if response.get("code") != 0 or "data" not in response:
                await msg.edit("**не удалось скачать**")
                return

            data = response["data"]
            images = data.get("images") or []
            video_url = data.get("play")
            music_url = data.get("music")

            if images:
                files = []
                for img_url in images:
                    try:
                        img_data = requests.get(img_url, headers=headers, timeout=10).content
                        if len(img_data) < 1000:
                            continue
                        tmp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                        tmp_img.write(img_data)
                        tmp_img.close()
                        files.append(tmp_img.name)
                    except:
                        continue

                if files:
                    await client.send_file(event.chat_id, files, caption="**альбом фото из TikTok**", reply_to=event.id)
                    for f in files:
                        os.remove(f)
                else:
                    await msg.edit("**не удалось загрузить изображения**")
                await msg.delete()
                return

            if video_url:
                video_data = requests.get(video_url, headers=headers, timeout=10).content
                if len(video_data) < 5000:
                    await msg.edit("**видео слишком короткое или пустое**")
                    return

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                    tmp_video.write(video_data)
                    tmp_path = tmp_video.name

                await client.send_file(event.chat_id, tmp_path, caption="**видео без водяного знака**", reply_to=event.id)
                os.remove(tmp_path)

            if music_url:
                audio_data = requests.get(music_url, headers=headers, timeout=10).content
                if len(audio_data) > 1000:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                        tmp_audio.write(audio_data)
                        tmp_audio_path = tmp_audio.name

                    await client.send_file(event.chat_id, tmp_audio_path, caption="**аудио из видео**", reply_to=event.id)
                    os.remove(tmp_audio_path)

            await msg.delete()

        except Exception as e:
            await msg.edit(f"**ошибка: {e}**")