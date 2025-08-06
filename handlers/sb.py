import re
import asyncio
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.sb$"))
    async def check_spambot_status(event):
        try:
            text = await fetch_spambot_text(client)
            result = analyze_spambot_text(text)
            await event.respond(result)
        except asyncio.TimeoutError:
            await event.respond("**спам-бот не отвечает, попробуй позже**")
        except Exception as e:
            await event.respond(f"**ошибка:** `{e}`")

async def fetch_spambot_text(client):
    async with client.conversation("SpamBot", timeout=15) as conv:
        await conv.send_message("/start")
        response = await conv.get_response()
        return response.text.lower()

def analyze_spambot_text(text):
    no_limits = [
        "ваш аккаунт свободен", "не имеет ограничений", "не має жодних обмежень",
        "вільний від будь-яких обмежень", "free from any restrictions", 
        "no limitations", "you don’t have any limitations", 
        "at the moment your account has no limitations"
    ]

    permanent_blocks = [
        "пока действуют ограничения", "вы не сможете писать тем", 
        "ограничен по ошибке", "не сможете приглашать",
        "sometimes our antispam system is too strict"
    ]

    temporary_limits = [
        "через", "після", "after", "until", "до", "again after", 
        "вы сможете снова писать", "ви зможете знову писати", 
        "you will be able to message"
    ]

    if any(p in text for p in no_limits):
        return "**аккаунт свободен от ограничений**"

    if any(p in text for p in permanent_blocks) and not any(p in text for p in temporary_limits):
        return "**вечный спам-блок: ограничения без срока окончания**"

    for phrase in temporary_limits:
        if phrase in text:
            snippet = text[text.find(phrase):]
            date_match = re.search(r"\d{1,2}[./-]\d{1,2}[./-]\d{2,4}(?:[, ]+\d{1,2}[:.]\d{2})?", snippet)
            if date_match:
                return f"**ограничения до:** `{date_match.group(0)}`"

    return "**ограничения активны, но дата не определена — проверь сам**"