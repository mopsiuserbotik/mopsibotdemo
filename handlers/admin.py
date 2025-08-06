import asyncio
from telethon import events, functions, types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsBanned, InputPeerUser

def register(client):

    async def get_input_peer(client, user_id):
        try:
            user = await client.get_entity(user_id)
            return InputPeerUser(user.id, user.access_hash)
        except:
            return None

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.h$"))
    async def show_muted_and_banned(event):
        chat = await event.get_chat()
        muted_users = []
        banned_users = []

        async for user in client.iter_participants(chat, filter=ChannelParticipantsBanned):
            try:
                participant = await client(functions.channels.GetParticipantRequest(chat, user.id))
                rights = participant.participant.banned_rights
                if isinstance(rights, ChatBannedRights):
                    if rights.send_messages:
                        muted_users.append(f"{user.id} - {user.first_name or 'NoName'}")
                    else:
                        banned_users.append(f"{user.id} - {user.first_name or 'NoName'}")
            except:
                continue

        msg = " **В муте**:\n" + ("\n".join(muted_users) if muted_users else "Нет") + "\n\n"
        msg += " **Забанены**:\n" + ("\n".join(banned_users) if banned_users else "Нет")
        await event.respond(msg)

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.mute"))
    async def mute_user(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            peer = await get_input_peer(client, reply.sender_id)
            if not peer:
                await event.respond("**Не могу получить пользователя.**")
                return
            try:
                await client(EditBannedRequest(
                    channel=chat,
                    participant=peer,
                    banned_rights=ChatBannedRights(
                        send_messages=True,
                        until_date=None,
                        view_messages=None,
                        send_media=None,
                        send_stickers=None,
                        send_gifs=None,
                        send_games=None
                    )
                ))
            except Exception as e:
                await event.respond(f"**Ошибка в mute: {e}**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.unmute"))
    async def unmute_user(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            peer = await get_input_peer(client, reply.sender_id)
            if not peer:
                await event.respond("**Не могу получить пользователя.**")
                return
            try:
                await client(EditBannedRequest(
                    channel=chat,
                    participant=peer,
                    banned_rights=ChatBannedRights(
                        send_messages=False,
                        until_date=None
                    )
                ))
            except Exception as e:
                await event.respond(f"**Ошибка в unmute: {e}**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.ban"))
    async def ban_user(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            peer = await get_input_peer(client, reply.sender_id)
            if not peer:
                await event.respond("**Не могу получить пользователя.**")
                return
            try:
                await client(EditBannedRequest(
                    channel=chat,
                    participant=peer,
                    banned_rights=ChatBannedRights(
                        view_messages=True,
                        until_date=None
                    )
                ))
            except Exception as e:
                await event.respond(f"**Ошибка в ban: {e}**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.unban"))
    async def unban_user(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            peer = await get_input_peer(client, reply.sender_id)
            if not peer:
                await event.respond("**Не могу получить пользователя.**")
                return
            try:
                await client(EditBannedRequest(
                    channel=chat,
                    participant=peer,
                    banned_rights=ChatBannedRights(
                        view_messages=False,
                        until_date=None
                    )
                ))
            except Exception as e:
                await event.respond(f"**Ошибка в unban: {e}**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.kick"))
    async def kick_user(event):
        chat = await event.get_chat()
        reply = await event.get_reply_message()
        if reply and reply.sender_id:
            peer = await get_input_peer(client, reply.sender_id)
            if not peer:
                await event.respond("**Не могу получить пользователя.**")
                return
            try:
                await client.kick_participant(chat, peer)
            except Exception as e:
                await event.respond(f"**Ошибка в kick: {e}**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.dmu$"))
    async def delete_user_messages(event):
        try:
            reply = await event.get_reply_message()
            if not reply or not reply.sender_id:
                await event.respond(" **ответь на сообщение человека.**")
                return

            chat = await event.get_chat()
            user_id = reply.sender_id
            deleted = 0

            async for msg in client.iter_messages(chat, from_user=user_id):
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.01)
                except:
                    continue

            await event.respond(f" **Удалено сообщений от типа**: {deleted}")
        except Exception as e:
            await event.respond(f" **Ошибка в .dmu**: {e}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.kill$"))
    async def kill_all(event):
        chat = await event.get_chat()
        kicked = 0
        async for user in client.iter_participants(chat):
            try:
                peer = await get_input_peer(client, user.id)
                if not peer or user.bot:
                    continue
                await client.kick_participant(chat, peer)
                kicked += 1
                await asyncio.sleep(0.1)
            except:
                continue
        await event.respond(f" **кикнуто: {kicked} участников**")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.delu$"))
    async def delete_deleted_users(event):
        chat = await event.get_chat()
        deleted = 0
        async for user in client.iter_participants(chat):
            if user.deleted:
                try:
                    peer = await get_input_peer(client, user.id)
                    if not peer:
                        continue
                    await client.kick_participant(chat, peer)
                    deleted += 1
                    await asyncio.sleep(0.1)
                except:
                    continue
        await event.respond(f" **удалено удалённых**: {deleted}")

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.banall$"))
    async def ban_all(event):
        chat = await event.get_chat()
        sender = await event.get_sender()
        me = sender.id

        banned = 0
        async for user in client.iter_participants(chat):
            if getattr(user, "bot", False) or user.id == me:
                continue
            try:
                peer = await get_input_peer(client, user.id)
                if not peer:
                    continue
                await client(EditBannedRequest(
                    channel=chat,
                    participant=peer,
                    banned_rights=ChatBannedRights(
                        until_date=None,
                        view_messages=True
                    )
                ))
                banned += 1
                await asyncio.sleep(0.5)
            except Exception as e:
                await event.respond(f"**ошибка при бане {user.id}: {e}**")
                break

        await event.respond(f"**забанили: {banned} участников**")