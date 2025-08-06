import os
import re
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.mv (.+)", func=lambda e: e.is_reply))
    async def mv_handler(event):
        new_name = event.pattern_match.group(1).strip()
        reply = await event.get_reply_message()

        if not reply.file:
            await event.respond("**нужен файл в ответе**")
            return

        if re.search(r'[\\/:\*\?"<>\|]', new_name):
            await event.respond("**имя содержит недопустимые символы**")
            return

        try:
            path = await reply.download_media()
            ext = os.path.splitext(path)[1]
            new_path = f"{new_name}{ext}"

            os.rename(path, new_path)
            await event.respond(file=new_path)
            os.remove(new_path)
        except Exception as e:
            await event.respond(f"**ошибка при переименовании:** `{e}`")