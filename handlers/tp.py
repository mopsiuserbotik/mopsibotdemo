import asyncio
from telethon import events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageTypingAction

typing_chats = {}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tp$"))
    async def start_typing(event):
        chat_id = event.chat_id
        if chat_id in typing_chats:
            return
        typing_chats[chat_id] = True
        await event.delete()

        while typing_chats.get(chat_id):
            try:
                await client(SetTypingRequest(
                    peer=chat_id,
                    action=SendMessageTypingAction()
                ))
                await asyncio.sleep(4)
            except Exception as e:
                print(f"[TP] **Ошибка**: {e}")
                break

        typing_chats.pop(chat_id, None)

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.tp off$"))
    async def stop_typing(event):
        chat_id = event.chat_id
        if chat_id in typing_chats:
            typing_chats[chat_id] = False
        await event.delete()