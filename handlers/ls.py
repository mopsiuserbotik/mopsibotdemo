import os
import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ls(?: (.+))?"))
    async def list_files(event):
        await asyncio.sleep(0.15)
        arg = event.pattern_match.group(1)
        paths = [arg.strip()] if arg else [os.getcwd(), "/storage/emulated/0"]

        output = ""
        for path in paths:
            if not os.path.exists(path):
                output += f"**путь не найден:** {path}\n\n"
                continue

            try:
                entries = os.listdir(path)
                if not entries:
                    output += f"{path}\n(пусто)\n\n"
                    continue

                dirs = [f"{name}/" for name in entries if os.path.isdir(os.path.join(path, name))]
                files = [name for name in entries if os.path.isfile(os.path.join(path, name))]
                output += f"{path}\n" + "\n".join(dirs + files) + "\n\n"
            except Exception as e:
                output += f"**ошибка при доступе к** {path}: {e}\n\n"

        await event.respond(output.strip())