import os
import datetime
import asyncio
from telethon import events
from telethon.tl.functions.contacts import GetContactsRequest

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.pch (-?\d+)$"))
    async def parse_chat(event):
        chat_id = int(event.pattern_match.group(1))
        await event.respond("**парсинг чата, занимает время...**")

        try:
            participants = await client.get_participants(chat_id)
            msg_counts = {}

            async for msg in client.iter_messages(chat_id, limit=None):
                if msg.sender_id:
                    msg_counts[msg.sender_id] = msg_counts.get(msg.sender_id, 0) + 1

            filename = f"chat_export_{chat_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = "/storage/emulated/0/Download"
            full_path = os.path.join(path, filename)

            if not os.path.exists(path):
                await event.respond("**папка загрузок не найдена. проверь разрешения Termux: `termux-setup-storage`**")
                return

            with open(full_path, "w", encoding="utf-8") as f:
                for user in participants:
                    uid = user.id
                    name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
                    username = f"@{user.username}" if user.username else "—"
                    phone = user.phone or "—"
                    count = msg_counts.get(uid, 0)

                    f.write(f"{name}\n{uid}\n{username}\n{phone}\nСообщений: {count}\n\n")

            await event.respond(f"**готово. файл сохранён в** `Download/{filename}`")

        except Exception as e:
            await event.respond(f"**ошибка при парсинге**: {e}")