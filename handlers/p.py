import re
import asyncio
from telethon import events, functions
from telethon.tl.types import PeerChannel

def register(client):
    post_watch_targets = set()

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.p (-?\d+) (on|off)$"))
    async def toggle_post_watcher(event):
        await asyncio.sleep(0.15)
        await event.delete()
        channel_id = int(event.pattern_match.group(1))
        state = event.pattern_match.group(2)

        if state == "on":
            post_watch_targets.add(channel_id)
            print(f"[~] Слежка включена за {channel_id}")
        else:
            post_watch_targets.discard(channel_id)
            print(f"[~] Слежка отключена за {channel_id}")

    @client.on(events.NewMessage())
    async def watch_channel_posts(event):
        await asyncio.sleep(0.15)
        if event.chat_id not in post_watch_targets:
            return

        text = event.raw_text
        links = re.findall(r"https?://[^\s]+", text)

        for link in links:
            try:
                print(f"[~] Найдена ссылка: {link}")
                slug = link.split("/")[-1].replace("+", "").strip()

                try:
                    await client(functions.messages.ImportChatInviteRequest(slug))
                    print(f"[+] Подана заявка или вступил по ссылке: {link}")
                except Exception as e1:
                    try:
                        entity = await client.get_entity(link)
                        await client(functions.channels.JoinChannelRequest(entity))
                        print(f"[+] Присоединился к: {link}")
                    except Exception as e2:
                        print(f"[!] Не удалось присоединиться по ссылке {link}: {e2}")
            except Exception as e:
                print(f"[!] Ошибка обработки ссылки {link}: {e}")