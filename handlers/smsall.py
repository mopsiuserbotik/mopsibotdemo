import asyncio
from telethon import events, types

def register(client):
    @client.on(events.NewMessage(pattern=r"\.smsall(?: (.+))?", outgoing=True))
    async def handler(event):
        await event.respond("**рассылаю сообщение...**")
        me = await client.get_me()
        count = 0

        try:
            message_to_send = None
            reply = await event.get_reply_message()

            if reply:
                message_to_send = reply
            elif event.pattern_match.group(1):
                message_to_send = event.pattern_match.group(1)
            else:
                await event.respond("**укажи текст или ответь на сообщение**")
                return

            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                if isinstance(entity, types.User) and not entity.bot and not entity.deleted and entity.id != me.id:
                    try:
                        if isinstance(message_to_send, str):
                            await client.send_message(entity.id, message_to_send)
                        else:
                            await client.send_file(entity.id, file=message_to_send.media, caption=(message_to_send.message or ""))
                        count += 1
                        await asyncio.sleep(1.2)
                    except Exception as e:
                        print(f"[smsall] пропущен {entity.id}: {e}")
                        continue

            await event.respond(f"**сообщение разослано {count} людям**")
        except Exception as e:
            await event.respond(f"**ошибка:** {e}")