import asyncio
from telethon import events
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors import (
    UserAlreadyParticipantError,
    InviteRequestSentError,
    ChatWriteForbiddenError,
)

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.send\s"))
    async def send_handler(event):
        await asyncio.sleep(0.05)

        parts = event.raw_text.split(None, 2)
        if len(parts) < 2:
            await event.respond("**использование:** `.send ID или юзернейм текст`")
            return

        target = parts[1]
        message = parts[2] if len(parts) > 2 else None
        reply = await event.get_reply_message()

        try:
            if target.startswith("@"):
                try:
                    await client(JoinChannelRequest(target))
                except UserAlreadyParticipantError:
                    pass
                except InviteRequestSentError:
                    await event.respond("**в чат подать заявку можно, но писать нельзя**")
                    return
                except ChatWriteForbiddenError:
                    await event.respond("**это канал или туда нельзя писать**")
                    return
                except Exception:
                    pass

            entity = await client.get_input_entity(
                int(target) if target.startswith("-100") else target
            )

        except Exception as e:
            await event.respond(f"**ошибка определения цели:** {e}")
            return

        try:
            if message:
                await client.send_message(entity, message)
            elif reply:
                await reply.forward_to(entity)
            else:
                await event.respond("**нет текста и нет ответа на сообщение для пересылки**")
                return

            await event.respond("**сообщение отправлено.**")
        except Exception as e:
            await event.respond(f"**ошибка отправки:** {e}")