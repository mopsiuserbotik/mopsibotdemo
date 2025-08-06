from telethon import events
import os
import asyncio

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.of(?: (.+))?"))
    async def send_file_from_path(event):
        arg = event.pattern_match.group(1)

        if not arg:
            await event.respond("**укажи имя файла или путь к файлу**")
            return

        arg = arg.strip()
        file_path = None

        if os.path.isfile(arg):
            file_path = arg
        else:
            await event.respond("**ищу файл во всех папках...**")
            for root, _, files in os.walk("."):
                if arg in files:
                    file_path = os.path.join(root, arg)
                    break

        if not file_path:
            await event.respond("**файл не найден**")
            return

        try:
            await client.send_file(event.chat_id, file_path, reply_to=event.reply_to_msg_id)
            await event.delete()
        except Exception as e:
            await event.respond(f"**ошибка:** {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.rm(?: (.+))?"))
    async def termux_rm(event):
        arg = event.pattern_match.group(1)

        if not arg:
            await event.respond("**укажи имя или путь файла/папки**")
            return

        path = arg.strip()
        full_paths = []

        if os.path.exists(path):
            full_paths.append(path)
        else:
            for base in ["/storage/emulated/0", "/sdcard", os.getcwd()]:
                for root, dirs, files in os.walk(base):
                    for name in dirs + files:
                        if name.lower() == path.lower():
                            full_paths.append(os.path.join(root, name))

        if not full_paths:
            await event.respond("**ничего не найдено**")
            return

        deleted = []
        failed = []

        for p in full_paths:
            try:
                proc = await asyncio.create_subprocess_exec("rm", "-rf", p,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL)
                await proc.communicate()
                (deleted if not os.path.exists(p) else failed).append(p)
            except Exception as e:
                failed.append(f"{p} ({e})")

        if deleted:
            await event.respond("\n".join(f"** удалено:** {p}" for p in deleted))
        if failed:
            await event.respond("\n".join(f" **не удалено:** {p}" for p in failed))

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sf(?: (.+))?"))
    async def save_file_to_path(event):
        input_path = event.pattern_match.group(1)
        default = "/storage/emulated/0/Download" if os.path.isdir("/storage/emulated/0/Download") else "./downloads"
        path = input_path.strip() if input_path else default
        os.makedirs(path, exist_ok=True)

        if not event.is_reply:
            await event.respond("**команда должна быть ответом на сообщение с файлом.**")
            return

        if not os.path.isdir(path):
            await event.respond("**указанная папка не найдена.**")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.respond("**ответь на сообщение с файлом.**")
            return

        try:
            file = await client.download_media(reply.media, file=path)
            await event.respond(f"**файл сохранён в** `{file}`")
        except Exception as e:
            await event.respond(f"**ошибка:** {e}")