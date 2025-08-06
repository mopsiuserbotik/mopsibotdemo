from telethon import events
from telethon.tl.types import InputPeerChannel, MessageMediaPhoto
import asyncio

def register(client):
    client.add_event_handler(grab_handler, events.NewMessage(pattern=r'^\.grab ([^\s]+) ([\w,]+)$'))

async def grab_handler(event):
    source, filters_raw = event.pattern_match.groups()
    filters = [f.lower() for f in filters_raw.split(",")]

    try:
        if source.startswith("-100") and source[1:].isdigit():
            channel_id = int(source)
            entity = await event.client.get_entity(channel_id)
            input_peer = InputPeerChannel(entity.id, entity.access_hash)
        else:
            input_peer = await event.client.get_entity(source)
    except Exception as e:
        return await event.respond(f"**ошибка:** не удалось найти пользователя или чат\n`{e}`")

    count = 0
    async for msg in event.client.iter_messages(input_peer, limit=500):
        if not msg.media and 'text' not in filters:
            continue

        matched = False
        if 'all' in filters:
            matched = True
        elif 'text' in filters and msg.message:
            matched = True
        elif 'photo' in filters and isinstance(msg.media, MessageMediaPhoto):
            matched = True
        elif 'video' in filters and (msg.video or (hasattr(msg.media, 'document') and msg.media.document.mime_type.startswith('video/'))):
            matched = True
        elif 'audio' in filters and (msg.audio or (hasattr(msg.media, 'document') and msg.media.document.mime_type.startswith('audio/'))):
            matched = True
        elif 'files' in filters and msg.document and not (msg.video or msg.audio):
            matched = True
        elif 'gs' in filters and getattr(msg, 'gif', False):
            matched = True
        elif 'vs' in filters and getattr(msg, 'video_note', False):
            matched = True

        if matched:
            try:
                await event.client.send_message(event.chat_id, msg, silent=True)
                count += 1
                await asyncio.sleep(0.2)
            except:
                continue

    await event.respond(f"**переслано сообщений:** {count}")