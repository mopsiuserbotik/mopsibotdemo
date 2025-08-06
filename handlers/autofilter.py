import os
import re
import json
import asyncio
from telethon import events, functions, types

autoban_words = set()
automute_words = set()

AUTOBAN_FILE = "autoban.json"
AUTOMUTE_FILE = "automute.json"

def load_words():
    if os.path.exists(AUTOBAN_FILE):
        with open(AUTOBAN_FILE, "r") as f:
            autoban_words.update(json.load(f))
    if os.path.exists(AUTOMUTE_FILE):
        with open(AUTOMUTE_FILE, "r") as f:
            automute_words.update(json.load(f))

def save_words():
    with open(AUTOBAN_FILE, "w") as f:
        json.dump(list(autoban_words), f)
    with open(AUTOMUTE_FILE, "w") as f:
        json.dump(list(automute_words), f)

load_words()

def contains_link(text):
    return bool(re.search(r"(https?://|t\.me/|telegram\.me/|www\.[^\s]+|[\w\-]+\.(com|net|org|ua|ru|top|xyz|info)\b)", text, re.IGNORECASE))

def register(client):
    @client.on(events.NewMessage(pattern=r"\.autoban(?: (.+))?", outgoing=True))
    async def handle_autoban(event):
        args = event.pattern_match.group(1)
        if not args:
            await event.respond("**укажи слова, `.autoban off` или `.autoban clean`**")
            return
        if args.lower() == "off":
            autoban_words.clear()
            save_words()
            await event.respond("**автобан отключён**")
            return
        if args.lower() == "clean":
            autoban_words.clear()
            if os.path.exists(AUTOBAN_FILE):
                os.remove(AUTOBAN_FILE)
            await event.respond("**список автобана очищен**")
            return
        words = [w.strip().lower() for w in args.split(",")]
        autoban_words.update(words)
        save_words()
        await event.respond(f"**бан за:** {', '.join(autoban_words)}")

    @client.on(events.NewMessage(pattern=r"\.automute(?: (.+))?", outgoing=True))
    async def handle_automute(event):
        args = event.pattern_match.group(1)
        if not args:
            await event.respond("**укажи слова, `.automute off` или `.automute clean`**")
            return
        if args.lower() == "off":
            automute_words.clear()
            save_words()
            await event.respond("**автомут отключён**")
            return
        if args.lower() == "clean":
            automute_words.clear()
            if os.path.exists(AUTOMUTE_FILE):
                os.remove(AUTOMUTE_FILE)
            await event.respond("**список автомута очищен**")
            return
        words = [w.strip().lower() for w in args.split(",")]
        automute_words.update(words)
        save_words()
        await event.respond(f"**мут за:** {', '.join(automute_words)}")

    @client.on(events.NewMessage(incoming=True))
    async def auto_moderation(event):
        if not event.is_group or not event.text:
            return

        text = event.raw_text.lower()
        user_id = event.sender_id
        chat = await event.get_input_chat()

        try:
            user = await client.get_input_entity(user_id)
        except:
            return

        async def ban():
            try:
                await event.delete()
                await client(functions.channels.EditBannedRequest(
                    channel=chat,
                    participant=user,
                    banned_rights=types.ChatBannedRights(until_date=None, view_messages=True)
                ))
                msg = "**Забанен за ссылку**" if contains_link(text) else "**Забанен за запрещённое слово**"
                await event.respond(msg)
            except:
                pass

        async def mute():
            try:
                await event.delete()
                await client(functions.channels.EditBannedRequest(
                    channel=chat,
                    participant=user,
                    banned_rights=types.ChatBannedRights(until_date=None, send_messages=True)
                ))
                msg = "**Замучен за ссылку**" if contains_link(text) else "**Замучен за запрещённое слово**"
                await event.respond(msg)
            except:
                pass

        if "ссылки" in autoban_words and contains_link(text):
            await ban()
            return

        if "ссылки" in automute_words and contains_link(text):
            await mute()
            return

        for word in autoban_words:
            if word != "ссылки" and word in text:
                await ban()
                return

        for word in automute_words:
            if word != "ссылки" and word in text:
                await mute()
                return

        await asyncio.sleep(0.15)