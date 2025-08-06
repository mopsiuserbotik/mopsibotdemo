from telethon.tl.functions.account import GetAuthorizationsRequest
from telethon import events
from datetime import datetime

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.sessions$'))
    async def list_sessions(event):
        try:
            result = await client(GetAuthorizationsRequest())
            sessions = result.authorizations
            if not sessions:
                await event.respond("**активных сессий не найдено**")
                return

            text = "**активные сессии:**\n\n"
            for s in sessions:
                platform = s.platform or "неизв."
                device = s.device_model or "неизв."
                country = s.country or "неизв."
                active = datetime.utcfromtimestamp(s.date_active.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
                current = " (текущая)" if s.current else ""
                text += f" {platform} | {device}{current}\n  **локация**: {country}\n  **активен**: {active}\n\n"

            await event.respond(text.strip())
        except Exception as e:
            await event.respond(f"**ошибка получения сессий:** {e}")