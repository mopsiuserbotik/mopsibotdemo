from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.errors import UsernameOccupiedError, UsernameInvalidError

def register(client):
    @client.on(events.NewMessage(pattern=r"\.name (.+)"))
    async def set_name(event):
        name_text = event.pattern_match.group(1).strip()
        parts = name_text.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        try:
            await client(UpdateProfileRequest(first_name=first_name, last_name=last_name))
            await event.respond("**имя обновлено**")
        except Exception as e:
            await event.respond(f"**ошибка при обновлении имени:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.bio(?:\s+(.+))?"))
    async def set_bio(event):
        bio = event.pattern_match.group(1)
        if bio == "-":
            bio = ""
        elif bio is None:
            return await event.respond("**укажи текст био или '-' для удаления**")
        try:
            await client(UpdateProfileRequest(about=bio))
            msg = "**био удалено**" if not bio else "**био обновлено**"
            await event.respond(msg)
        except Exception as e:
            await event.respond(f"**ошибка при обновлении био:** {str(e)}")

    @client.on(events.NewMessage(pattern=r"\.username(?:\s+(.+))?"))
    async def set_username(event):
        username = event.pattern_match.group(1)
        if username == "-":
            username = ""
        elif username is None:
            return await event.respond("**укажи юзернейм или '-' для удаления**")
        else:
            username = username.strip()
        try:
            await client(UpdateUsernameRequest(username))
            msg = f"**юзернейм обновлён на @{username}**" if username else "**юзернейм удалён**"
            await event.respond(msg)
        except UsernameOccupiedError:
            await event.respond("**этот юзер уже занят**")
        except UsernameInvalidError:
            await event.respond("**недопустимый юзернейм**")
        except Exception as e:
            await event.respond(f"**ошибка:** {str(e)}")