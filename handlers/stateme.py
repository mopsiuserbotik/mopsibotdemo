from telethon import events, types
from datetime import datetime

def register(client):
    client.add_event_handler(stateme_handler, events.NewMessage(outgoing=True, pattern=r"\.stateme"))

async def stateme_handler(event):
    await event.respond("**собираю статистику...**")

    me = await event.client.get_me()
    dialogs = await event.client.get_dialogs()

    groups = sum(1 for d in dialogs if isinstance(d.entity, types.Channel) and getattr(d.entity, 'megagroup', False))
    channels = sum(1 for d in dialogs if isinstance(d.entity, types.Channel) and not getattr(d.entity, 'megagroup', False))
    private_chats = sum(1 for d in dialogs if isinstance(d.entity, types.User))

    msg_count = 0
    media_count = 0
    active_chats = set()

    async for message in event.client.iter_messages(me, limit=100000):
        msg_count += 1
        active_chats.add(message.chat_id)
        if message.media:
            media_count += 1

    last_seen = "неизвестно"
    if me.status:
        if isinstance(me.status, types.UserStatusOnline):
            last_seen = "сейчас онлайн"
        elif isinstance(me.status, types.UserStatusOffline):
            utc_time = me.status.was_online
            local_time = utc_time.astimezone()
            last_seen = local_time.strftime('%Y-%m-%d %H:%M:%S')

    text = (
        f"**статистика аккаунта:**\n"
        f"имя: {me.first_name or ''} {me.last_name or ''}\n"
        f"юзернейм: @{me.username or 'отсутствует'}\n"
        f"id: {me.id}\n"
        f"сообщений отправлено (до 100000): {msg_count}\n"
        f"чатов (личные): {private_chats}\n"
        f"групп: {groups}\n"
        f"каналов: {channels}\n"
        f"активных чатов (по сообщениям): {len(active_chats)}\n"
        f"сообщений с медиа: {media_count}\n"
        f"последний онлайн: {last_seen}"
    )

    await event.respond(text)