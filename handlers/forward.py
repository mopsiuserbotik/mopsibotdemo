from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.forward\s+@?(\w+)\s+(\d+)"))
    async def forward_from_target(event):
        target_username = event.pattern_match.group(1)
        count = int(event.pattern_match.group(2))

        if count < 1 or count > 100:
            await event.respond("**укажи количество от 1 до 100**")
            return

        try:
            source = await client.get_entity(target_username)
            messages = await client.get_messages(source, limit=count)
            message_ids = [msg.id for msg in messages if msg]

            await client.forward_messages(
                entity=event.chat_id,
                messages=message_ids[::-1],
                from_peer=source
            )

            await event.respond(f"**переслано {len(message_ids)} сообщений из @{target_username}**")
        except Exception as e:
            await event.respond(f"**ошибка:** `{e}`")