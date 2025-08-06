from telethon import events

def register(client):
    mirror_map = {}

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.mirror (-?\d+) (-?\d+) (on|off)$"))
    async def toggle_mirror(event):
        src = int(event.pattern_match.group(1))
        dst = int(event.pattern_match.group(2))
        state = event.pattern_match.group(3).lower()
        key = (src, dst)

        if state == "off":
            if key in mirror_map:
                mirror_map.pop(key)
                await event.respond(f"**зеркалирование отключено:** {src} → {dst}")
            else:
                await event.respond("**зеркалирование не активно**")
            return

        mirror_map[key] = True
        await event.respond(f"**зеркалирование включено:** {src} → {dst}")

    @client.on(events.NewMessage)
    async def mirror_forward(event):
        for (source, target) in mirror_map:
            if event.chat_id == source and not event.is_private:
                try:
                    await event.forward_to(target)
                except Exception as e:
                    print(f"[mirror] ошибка: {e}")