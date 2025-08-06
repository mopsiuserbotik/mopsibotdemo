import asyncio
from telethon import events

def register(client):
    mock_reply_map = {}

    async def get_user_from_input(event, text):
        try:
            if text.startswith("@"):
                async for user in client.iter_participants(event.chat_id, search=text[1:]):
                    if user.username and user.username.lower() == text[1:].lower():
                        return user
            else:
                return await client.get_entity(int(text))
        except:
            return None

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.mockreply(?: (.+))?"))
    async def toggle_mockreply(event):
        args = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        await event.delete()

        if args is None and not reply:
            await event.respond("**используй в ответ или с @юзером**: `.mockreply привет,пока on`")
            return

        args = args or ""
        parts = args.strip().split()
        text_lower = args.lower()

        if text_lower.endswith("off"):
            if reply:
                try:
                    sender = await reply.get_sender()
                    uid = sender.id
                except:
                    await event.respond("**не удалось получить пользователя**")
                    return
            elif parts:
                user = await get_user_from_input(event, parts[0])
                if not user:
                    await event.respond("**не найден**")
                    return
                uid = user.id
            else:
                await event.respond("**не указан пользователь**")
                return

            if uid in mock_reply_map:
                del mock_reply_map[uid]
                await event.respond(f"**отключён автоответ для** {uid}")
            else:
                await event.respond("**у пользователя не было автоответа**")
            return

        if text_lower.endswith("on"):
            phrases_raw = args.rsplit("on", 1)[0].strip()
            phrases = [x.strip() for x in phrases_raw.split(",") if x.strip()]

            if not phrases:
                await event.respond("**нет фраз**")
                return

            if reply:
                try:
                    sender = await reply.get_sender()
                    uid = sender.id
                except:
                    await event.respond("**не удалось получить отправителя**")
                    return
            elif parts:
                user = await get_user_from_input(event, parts[0])
                if not user:
                    await event.respond("**не найден**")
                    return
                uid = user.id
            else:
                await event.respond("**укажи кого**")
                return

            mock_reply_map[uid] = {"phrases": phrases, "index": 0}
            await event.respond(f"**автоответ включён для** {uid} ({len(phrases)} **фраз**)")
            return

        await event.respond("**непонятный формат**")

    @client.on(events.NewMessage(incoming=True))
    async def auto_mock_reply(event):
        uid = event.sender_id
        if uid in mock_reply_map:
            try:
                data = mock_reply_map[uid]
                await event.reply(data["phrases"][data["index"]])
                data["index"] = (data["index"] + 1) % len(data["phrases"])
            except:
                pass