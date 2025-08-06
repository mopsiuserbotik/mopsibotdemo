from telethon import events
from telethon.tl.functions.messages import DeleteHistoryRequest, DeleteMessagesRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel, User, Chat, Channel
import asyncio

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.wipeaccount$"))
    async def wipe_account(event):
        await asyncio.sleep(0.1)
        await event.respond("**Очистка аккаунта...**")

        try:
            me = await client.get_me()
            my_id = me.id

            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                chat_id = dialog.id

                if isinstance(entity, User) and entity.is_self:
                    continue

                try:
                    async for msg in client.iter_messages(chat_id, from_user='me'):
                        await client(DeleteMessagesRequest(peer=chat_id, id=[msg.id], revoke=True))
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"[!] **Ошибка при удалении своих сообщений в** {chat_id}: {e}")

                try:
                    await client(DeleteHistoryRequest(peer=chat_id, max_id=0, revoke=True))
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"[!] **Ошибка при удалении истории в** {chat_id}: {e}")

                try:
                    if isinstance(entity, (Chat, Channel)):
                        await client(LeaveChannelRequest(chat_id))
                        await asyncio.sleep(0.15)
                except Exception as e:
                    print(f"[!] **Ошибка при выходе из** {chat_id}: {e}")

            await event.respond("**Аккаунт полностью очищен.**")

        except Exception as e:
            await event.respond(f"**Ошибка:** {e}")