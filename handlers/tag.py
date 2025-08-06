import random
import asyncio
from telethon import events, utils
from telethon.tl.types import ChannelParticipantsSearch

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tag (all|\d+)$"))
    async def tag_users(event):
        mode = event.pattern_match.group(1)
        chat = await event.get_input_chat()

        try:
            participants = []
            async for user in client.iter_participants(chat, filter=ChannelParticipantsSearch('')):
                if user.bot or user.deleted or (not user.username and not user.first_name):
                    continue
                participants.append(user)

            if not participants:
                return await event.respond("**нет подходящих участников**")

            if mode == "all":
                users_to_tag = participants
            else:
                count = int(mode)
                if count <= 0:
                    return await event.respond("**укажи число больше 0**")
                users_to_tag = random.sample(participants, min(count, len(participants)))

            chunk_size = 5
            mentions = [
                f"[{utils.get_display_name(u)}](tg://user?id={u.id})"
                for u in users_to_tag
            ]

            for i in range(0, len(mentions), chunk_size):
                await event.respond(" ".join(mentions[i:i + chunk_size]))
                await asyncio.sleep(1.2)

            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка:** {str(e)[:150]}")