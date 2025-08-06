import asyncio
from telethon import events
from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.panic$"))
    async def panic_reset(event):
        await event.respond("**сбрасываем профиль**...")

        try:
            await client(UpdateProfileRequest(first_name="mopsi user", last_name="", about=""))

            photos = await client(GetUserPhotosRequest(user_id="me", offset=0, max_id=0, limit=1000))
            if photos.photos:
                await client(DeletePhotosRequest(id=photos.photos))

            await event.respond("**профиль сброшен**.")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка при сбросе**: {e}")