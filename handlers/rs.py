import asyncio
from telethon import events, errors

rs_task = None
rs_config = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.rs(?: (.+))?$"))
    async def handle_rs(event):
        global rs_task, rs_config
        await event.delete()

        text = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not text:
            await event.respond("**пример:** `.rs -10012345 Текст 3 on` или `.rs -10012345 3 on` (в ответ на сообщение)")
            return

        args = text.strip().split()
        if not args:
            await event.respond("**ошибка: нет аргументов**")
            return

        state = args[-1].lower()
        if state not in ("on", "off"):
            await event.respond("**последний аргумент должен быть 'on' или 'off'**")
            return

        if state == "off":
            if rs_task:
                rs_task.cancel()
                rs_task = None
                await event.respond("**рассылка остановлена.**")
            else:
                await event.respond("**рассылка уже отключена.**")
            return

        args = args[:-1]
        if not args:
            await event.respond("**укажи ID чатов и интервал**")
            return

        chat_ids_raw = args[0]
        try:
            chat_ids = [int(cid) for cid in chat_ids_raw.split(",") if cid]
        except Exception as e:
            await event.respond(f"**ошибка в ID чатов:** {e}")
            return

        if len(args) == 2 and reply:
            try:
                interval = int(args[1])
                text_to_send = None
            except:
                await event.respond("**интервал должен быть числом**")
                return
        elif len(args) >= 3:
            try:
                interval = int(args[-1])
            except:
                await event.respond("**интервал должен быть числом**")
                return
            text_to_send = " ".join(args[1:-1])
        else:
            await event.respond("**неверный формат аргументов**")
            return

        if interval <= 0:
            await event.respond("**интервал должен быть больше 0**")
            return

        if rs_task:
            rs_task.cancel()

        rs_config = {
            "chat_ids": chat_ids,
            "text": text_to_send,
            "interval": interval,
            "reply": reply
        }

        await event.respond(f"**рассылка включена**\nчаты: `{chat_ids}`\nинтервал: `{interval}` мин")
        rs_task = asyncio.create_task(repeat_sender_loop(client, event))


async def repeat_sender_loop(client, origin_event):
    global rs_task, rs_config

    try:
        while True:
            for chat_id in rs_config["chat_ids"]:
                try:
                    if rs_config["reply"]:
                        msg = rs_config["reply"]
                        if msg.media:
                            await client.send_file(chat_id, msg.media, caption=msg.message or "")
                        else:
                            await client.send_message(chat_id, msg.message or "")
                    else:
                        await client.send_message(chat_id, rs_config["text"])
                    print(f"[→] отправлено в {chat_id}")
                except errors.FloodWaitError as e:
                    print(f"[×] floodwait в {chat_id}: {e.seconds} сек")
                    await asyncio.sleep(e.seconds + 1)
                except Exception as e:
                    print(f"[×] ошибка в {chat_id}: {e}")
            await asyncio.sleep(rs_config["interval"] * 60)
    except asyncio.CancelledError:
        print("[×] задача рассылки остановлена.")
    except Exception as e:
        rs_task = None
        await origin_event.respond(f"**фатальная ошибка рассылки:** {e}")