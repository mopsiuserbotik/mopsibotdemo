from telethon import events

sc_targets = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sc(?:\s+(@?\w+|\d+))?\s*(on|off)$"))
    async def toggle_sc(event):
        global sc_targets
        chat_id = event.chat_id
        arg, state = event.pattern_match.group(1), event.pattern_match.group(2)

        if state == "off":
            sc_targets.pop(chat_id, None)
            return await event.respond("**уже не доедаем)**")

        if arg:
            try:
                entity = await client.get_entity(arg)
                sc_targets[chat_id] = entity.id
                return await event.respond("**доедаем)**")
            except:
                return await event.respond("**не удалось получить юзера**(")

        if event.is_reply:
            msg = await event.get_reply_message()
            if msg and msg.sender_id:
                sc_targets[chat_id] = msg.sender_id
                return await event.respond("**доедаем)**")

        return await event.respond("**укажи пользователя или ответь на сообщение**")

    @client.on(events.NewMessage)
    async def sc_handler(event):
        cid = event.chat_id
        if cid not in sc_targets or event.sender_id != sc_targets[cid]:
            return

        try:
            if event.fwd_from:
                await client.forward_messages(cid, event.id, cid)
            elif event.media:
                await client.send_file(
                    cid,
                    file=event.media,
                    caption=event.text or None,
                    voice_note=event.voice,
                    force_document=event.document and not event.video
                )
            elif event.poll:
                await client.send_message(cid, file=event.poll)
            else:
                await client.send_message(cid, event.text or " ")
        except Exception as e:
            print(f"[SC ERROR] {e}")