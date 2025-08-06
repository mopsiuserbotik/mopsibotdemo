from telethon import events, functions
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from PIL import Image
import os
import asyncio

def register(client):
    @client.on(events.NewMessage(pattern=r"\.clone(?:\s+@?([\w\d_]+))?$", outgoing=True))
    async def handler(event):
        await asyncio.sleep(0.15)
        await event.respond("**копирую профиль...**")

        user = None
        username = event.pattern_match.group(1)

        if username:
            try:
                user = await client.get_entity(username)
            except Exception as e:
                await event.respond(f"**не найден**: {e}")
                return
        elif event.is_reply:
            reply = await event.get_reply_message()
            user = await reply.get_sender()
        else:
            await event.respond("**укажи юзернейм или ответь на сообщение**")
            return

        try:
            full = await client(GetFullUserRequest(user.id))
            name = (user.first_name or "")[:64] or "."
            last = (user.last_name or "")[:64]
            about = (full.full_user.about or "")[:70]

            await client(functions.account.UpdateProfileRequest(
                first_name=name,
                last_name=last,
                about=about
            ))

            photos = await client.get_profile_photos(user.id, limit=10)
            if not photos:
                await event.respond("**аватарки не найдены**")
                await event.delete()
                return

            uploaded = 0
            for i, photo in enumerate(reversed(photos)):
                try:
                    path = f"profile_clone_{i}"
                    file = await client.download_media(photo, file=path)
                    if not file:
                        continue

                    ext = os.path.splitext(file)[1].lower()

                    if ext in [".mp4", ".mov"]:
                        await client(UploadProfilePhotoRequest(
                            video=await client.upload_file(file)
                        ))
                    else:
                        try:
                            img = Image.open(file)
                            if img.width < 160 or img.height < 160:
                                img = img.resize((160, 160), Image.LANCZOS)
                                img.save(file)
                            await client(UploadProfilePhotoRequest(
                                file=await client.upload_file(file)
                            ))
                        except:
                            continue

                    uploaded += 1
                    os.remove(file)
                    await asyncio.sleep(1.5)

                except:
                    continue

            await event.respond(f"**готово. ав загружено:** {uploaded}")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка:** {e}")