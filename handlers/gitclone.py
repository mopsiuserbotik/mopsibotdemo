import os
import asyncio
from urllib.parse import urlparse
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.gitclone (https?://[^\s]+)", outgoing=True))
    async def handler(event):
        url = event.pattern_match.group(1).strip()
        await event.respond("**клонирую репозиторий...**")

        repo_name = os.path.splitext(os.path.basename(urlparse(url).path))[0] or "repo"
        download_dir = "/storage/emulated/0/Download"
        fallback_dir = "./downloads"
        save_dir = download_dir if os.path.exists(download_dir) else fallback_dir

        os.makedirs(save_dir, exist_ok=True)
        target_path = os.path.join(save_dir, repo_name)

        if os.path.exists(target_path):
            await event.respond(f"**папка `{repo_name}` уже существует**, удалите или переименуйте.")
            return

        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "clone", url, target_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode == 0:
                await event.respond(f"**клонирование завершено. путь:** `{target_path}`")
            else:
                await event.respond(f"**ошибка при клонировании:**\n{stderr.decode().strip()}")

        except FileNotFoundError:
            await event.respond("**git не установлен, установи**")
        except Exception as e:
            await event.respond(f"**непредвиденная ошибка:** {e}")