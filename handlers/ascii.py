from telethon import events
from art import text2art

ascii_styles = [
    "block", "rnd-small", "random", "tarty1", "banner3-D", "cybermedium",
    "soft", "ghost", "big", "chunky", "epic", "fancy133", "weird",
    "graffiti", "3d", "cyberlarge", "avatar", "blocky", "doom", "slscript",
    "amcrazor", "twopoint", "xhelvi", "sub-zero", "fuzzy", "amcslash",
    "delta-corps-priest", "doh", "bulbhead", "acrobatic",
    "alligator", "amcrazo2", "charact1", "contessa", "drpepper", "isometric1",
    "isometric2", "isometric3", "isometric4", "larry3d", "nancyj", "pepper",
    "puffy", "rectangles", "roman", "smkeyboard", "starwars", "stampatello",
    "swampland", "thick", "twisted", "whimsy"
]

def register(client):
    @client.on(events.NewMessage(pattern=r"\.ascii (.+)", outgoing=True))
    async def ascii_handler(event):
        raw_input = event.pattern_match.group(1).strip()

        if raw_input.rsplit(" ", 1)[-1].isdigit():
            *text_parts, style_number = raw_input.rsplit(" ", 1)
            text = " ".join(text_parts)
            style_idx = int(style_number) - 1
        else:
            text = raw_input
            style_idx = 0

        if not text:
            await event.reply("**укажи текст для ASCII-арта**")
            return

        if style_idx < 0 or style_idx >= len(ascii_styles):
            await event.reply(f"**неверный номер стиля. используй от 1 до {len(ascii_styles)}**")
            return

        try:
            font = ascii_styles[style_idx]
            art = text2art(text, font=font)
            if len(art) > 4090:
                await event.reply("**результат слишком длинный для Telegram**")
                return
            await event.reply(f"**Стиль:** `{font}`\n```\n{art}\n```")
        except Exception as e:
            await event.reply(f"**ошибка при создании ASCII-арта:** {e}")