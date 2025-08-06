import re
import asyncio
from telethon import events
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import UserAlreadyParticipantError
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import PeerChannel

def register(client):
    @client.on(events.NewMessage(pattern=r"\.join (.+)", outgoing=True))
    async def handler(event):
        await asyncio.sleep(0.15)
        await event.delete()
        target = event.pattern_match.group(1).strip()

        try:
            match = re.search(r"(?:t\.me\/\+|joinchat\/|\+)([\w-]+)", target)
            if match:
                try:
                    await client(ImportChatInviteRequest(match.group(1)))
                    print("[join] **вступил**")
                except UserAlreadyParticipantError:
                    print("[join] **уже в этом чате**")
                return

            if re.match(r"^(@|https:\/\/t\.me\/)?[\w\d_]{5,}$", target):
                username = target.replace("https://t.me/", "").replace("@", "")
                entity = await client.get_entity(username)
                await client(JoinChannelRequest(entity))
                print(f"[join] **вступил в** @{username}")
                return

            if target.lstrip("-").isdigit():
                chat_id = int(target)
                entity = await client.get_entity(PeerChannel(chat_id))
                try:
                    await client(JoinChannelRequest(entity))
                    print(f"[join] **вступил в чат по ID** {chat_id}")
                except UserAlreadyParticipantError:
                    print(f"[join] **уже в этом чате**")
                return

            print("[join] **неверный формат**")
        except Exception as e:
            print(f"[join] **ошибка**: {e}")