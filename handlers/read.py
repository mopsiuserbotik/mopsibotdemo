from telethon import events

read_chats = set()
read_all = False

def register(client):
    client.add_event_handler(toggle_read, events.NewMessage(outgoing=True, pattern=r"\.read(?: all)?(?: (on|off))?$"))
    client.add_event_handler(read_incoming, events.NewMessage(incoming=True))

async def toggle_read(event):
    global read_all
    await event.delete()
    text = event.raw_text
    is_all = "all" in text
    arg = event.pattern_match.group(1)

    if arg == "on":
        if is_all:
            read_all = True
        else:
            read_chats.add(event.chat_id)
    elif arg == "off":
        if is_all:
            read_all = False
        else:
            read_chats.discard(event.chat_id)
    else:
        try:
            async for dialog in event.client.iter_dialogs():
                if dialog.unread_count > 0:
                    try:
                        await event.client.send_read_acknowledge(dialog.entity)
                    except:
                        continue
        except:
            pass

async def read_incoming(event):
    if event.out:
        return
    if read_all or event.chat_id in read_chats:
        try:
            await event.client.send_read_acknowledge(event.chat_id, max_id=event.id)
        except:
            pass