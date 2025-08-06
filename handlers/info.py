from telethon import events, types
from telethon.tl.functions.users import GetFullUserRequest
from datetime import timedelta, datetime

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.info$"))
    async def whois(event):
        await event.delete()

        if not event.is_reply:
            return await event.respond("**команда должна быть ответом на сообщение**")

        reply = await event.get_reply_message()
        user = await reply.get_sender()
        if not user or user.bot:
            return await event.respond("**пользователь не найден или это бот**")

        try:
            full = await client(GetFullUserRequest(user.id))

            name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
            username = f"@{user.username}" if user.username else "—"
            bio = full.full_user.about or "—"

            status = user.status
            if isinstance(status, types.UserStatusOnline):
                last_seen = "Сейчас онлайн"
            elif isinstance(status, types.UserStatusRecently):
                last_seen = "Был недавно"
            elif isinstance(status, types.UserStatusLastWeek):
                last_seen = "Был на этой неделе"
            elif isinstance(status, types.UserStatusLastMonth):
                last_seen = "Был в течение месяца"
            elif isinstance(status, types.UserStatusOffline):
                dt = status.was_online + timedelta(hours=3)
                last_seen = f"Был(а) в сети: {dt.strftime('%d.%m.%Y %H:%M:%S')} (UTC+3)"
            else:
                last_seen = "Статус скрыт"

            text = (
                f"<b>{name}</b>\n"
                f"<code>{user.id}</code>\n"
                f"<b>Username:</b> {username}\n"
                f"<b>О себе:</b> {bio}\n"
                f"<b>Статус:</b> {last_seen}"
            )

            await event.respond(text, parse_mode="html")

        except Exception as e:
            await event.respond(f"**ошибка:** {str(e)[:100]}")