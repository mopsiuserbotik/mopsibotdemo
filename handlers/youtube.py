import os
import re
from telethon import events
from yt_dlp import YoutubeDL

def register(client):

    def safe_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "", name)

    def extract_url(text):
        urls = re.findall(r'(https?://\S+)', text)
        return urls[0] if urls else None

    @client.on(events.NewMessage(pattern=r'^\.youtube(?: (.+))?$'))
    async def youtube(event):
        await event.reply("**загрузка видео и аудио...**")
        input_text = event.pattern_match.group(1)

        url = input_text or extract_url(event.raw_text)
        if not url and event.is_reply:
            reply = await event.get_reply_message()
            url = extract_url(reply.text or "")

        if not url:
            return await event.respond("**не найдена ссылка**")

        try:
            title = None

            ydl_opts_video = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': '/storage/emulated/0/Download/%(title)s.%(ext)s',
                'merge_output_format': 'mp4',
                'quiet': True
            }

            with YoutubeDL(ydl_opts_video) as ydl:
                info = ydl.extract_info(url, download=True)
                title = safe_filename(info.get("title", "video"))
                video_path = ydl.prepare_filename(info)

            ydl_opts_audio = {
                'format': 'bestaudio/best',
                'outtmpl': f'/storage/emulated/0/Download/{title}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True
            }

            with YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])
                audio_path = f"/storage/emulated/0/Download/{title}.mp3"

            if os.path.isfile(video_path):
                await client.send_file(event.chat_id, video_path, caption=f"**готово: {os.path.basename(video_path)}**")
                os.remove(video_path)
            else:
                await event.respond("**видео не найдено после загрузки**")

            if os.path.isfile(audio_path):
                await client.send_file(event.chat_id, audio_path, caption=f"**готово: {os.path.basename(audio_path)}**")
                os.remove(audio_path)
            else:
                await event.respond("**аудио не найдено после загрузки**")

        except Exception as e:
            await event.respond(f"**ошибка:** {e}")