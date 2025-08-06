import os
import zipfile
import rarfile
from telethon import events

def register(client):

    @client.on(events.NewMessage(pattern=r"\.(unzipf|unrarf)(?: (.+))?", outgoing=True))
    async def unpack_and_send_handler(event):
        await extract_archive(event, send_files=True)

    @client.on(events.NewMessage(pattern=r"\.(unzip|unrar)(?: (.+))?", outgoing=True))
    async def unpack_handler(event):
        await extract_archive(event, send_files=False)

    async def extract_archive(event, send_files=False):
        cmd = event.pattern_match.group(1)
        path = event.pattern_match.group(2)
        is_rar = 'rar' in cmd

        if not path and event.is_reply:
            reply = await event.get_reply_message()
            if reply.document:
                path = f"/sdcard/Download/{reply.file.name}"
                await reply.download_media(file=path)
            else:
                await event.respond("**ответь на архив или укажи путь**")
                return

        if not path:
            await event.respond("**укажи путь к архиву или ответь на файл**")
            return

        if not os.path.isfile(path):
            await event.respond(f"**файл не найден:** `{path}`")
            return

        extract_path = os.path.dirname(path)
        try:
            files_list = []
            if is_rar:
                if not rarfile.is_rarfile(path):
                    await event.respond("**это не RAR архив или он повреждён**")
                    return
                with rarfile.RarFile(path) as rf:
                    rf.extractall(extract_path)
                    files_list = rf.namelist()
            else:
                if not zipfile.is_zipfile(path):
                    await event.respond("**это не ZIP архив**")
                    return
                with zipfile.ZipFile(path) as zf:
                    zf.extractall(extract_path)
                    files_list = zf.namelist()

            if not files_list:
                await event.respond("**архив пустой**")
                return

            safe_files = []
            for f in files_list:
                try:
                    f_safe = f.encode('utf-8', 'ignore').decode('utf-8')
                    if len(f_safe) > 100:
                        f_safe = f_safe[:97] + "..."
                    safe_files.append(f_safe)
                except:
                    safe_files.append("[некорректное имя файла]")

            result = f"**Распаковано в:** `{extract_path}`\n**Файлы:**\n```{os.linesep.join(safe_files)}```"
            await event.respond(result)

            if send_files:
                for name in files_list:
                    abs_path = os.path.join(extract_path, name)
                    if os.path.isfile(abs_path):
                        try:
                            await event.respond(file=abs_path)
                        except:
                            await event.respond(f"**не удалось отправить:** `{name}`")

        except Exception as e:
            await event.respond(f"**ошибка при распаковке:** {e}")