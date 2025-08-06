import asyncio
import re
from telethon import events
from telethon.tl.types import PeerUser

bazz_targets = set()
bazz_private = set()

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.bazz(?:\s+@?([\w\d_]+))?$"))
    async def handler(event):
        await event.delete()
        chat_id = event.chat_id
        is_private = event.is_private

        try:
            if event.pattern_match.group(1):
                user = await client.get_entity(event.pattern_match.group(1))
            elif event.is_reply:
                reply = await event.get_reply_message()
                user = await reply.get_sender()
            else:
                print("**[BAZZ] Укажи юзернейм или ответь на сообщение**.")
                return
        except Exception as e:
            print(f"**[BAZZ] Ошибка получения юзера:** {e}")
            return

        if not user:
            print("**[BAZZ] Пользователь не найден**.")
            return

        mention = f"@{user.username}" if user.username else f"[user](tg://user?id={user.id})"

        if is_private:
            if chat_id in bazz_private:
                bazz_private.remove(chat_id)
                return
            bazz_private.add(chat_id)
            while chat_id in bazz_private:
                try:
                    msg = await client.send_message(chat_id, mention, parse_mode="md")
                    await asyncio.sleep(0.15)
                    await msg.delete()
                    await asyncio.sleep(0.25)
                except Exception as e:
                    print(f"**[BAZZ/PM] Ошибка:** {e}")
                    await asyncio.sleep(5)
        else:
            if chat_id in bazz_targets:
                bazz_targets.remove(chat_id)
                return
            bazz_targets.add(chat_id)
            while chat_id in bazz_targets:
                try:
                    msg = await client.send_message(chat_id, mention, parse_mode="md")
                    await asyncio.sleep(0.15)
                    await msg.delete()
                    await asyncio.sleep(0.25)
                except Exception as e:
                    print(f"**[BAZZ/GROUP] Ошибка:** {e}")
                    await asyncio.sleep(5)