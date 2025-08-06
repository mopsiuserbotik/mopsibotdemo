from telethon import events, types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.errors import FloodWaitError
from telethon.tl.types import ChatBannedRights, ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.tl.functions.channels import GetParticipantRequest
import asyncio

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.lock (on|off)$', outgoing=True))
    async def lock_handler(event):
        try:
            await event.delete()
            if not (event.is_group or event.is_channel):
                return

            me = await client.get_me()
            try:
                participant = await client(GetParticipantRequest(
                    channel=event.chat_id,
                    participant=me.id
                ))
                if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                    await event.reply("**так ты не админ лол**")
                    return
                if isinstance(participant.participant, ChannelParticipantAdmin):
                    if not participant.participant.admin_rights.ban_users:
                        await event.reply("**у тебя нету прав банить**")
                        return
            except Exception as e:
                await event.reply(f"**ошибка прав:** {e}")
                return

            mode = event.pattern_match.group(1)
            is_locking = mode == "on"
            action_text = "мут" if is_locking else "размут"

            msg = await event.reply(f"**{action_text} начал применяться...**")

            mute_rights = ChatBannedRights(
                until_date=None,
                send_messages=is_locking,
                send_media=is_locking,
                send_stickers=is_locking,
                send_gifs=is_locking,
                send_games=is_locking,
                send_inline=is_locking,
                embed_links=is_locking,
            )

            participants = []
            async for user in client.iter_participants(event.chat_id):
                try:
                    if not isinstance(user.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                        participants.append(user)
                except Exception:
                    continue

            count = 0
            for user in participants:
                try:
                    await client(EditBannedRequest(
                        channel=event.chat_id,
                        participant=user.id,
                        banned_rights=mute_rights
                    ))
                    count += 1
                    if count % 10 == 0:
                        await msg.edit(f"**{action_text} применён к {count} участникам...**")
                    await asyncio.sleep(0.5)
                except FloodWaitError as fwe:
                    await asyncio.sleep(fwe.seconds)
                except Exception as e:
                    print(f"Ошибка при изменении прав у пользователя {user.id}: {e}")

            await msg.edit(f"**{action_text} успешно применён к {count} участникам**")
            await asyncio.sleep(5)
            await msg.delete()

        except Exception as e:
            await event.reply(f"**ошибка:** {e}")