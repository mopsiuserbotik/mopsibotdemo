import os
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageOps
from telethon import events
from telethon.tl.types import MessageMediaPhoto

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.mem (.+)"))
    async def mem_handler(event):
        await asyncio.sleep(0.15)
        text = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not reply or not reply.media or not isinstance(reply.media, MessageMediaPhoto):
            await event.respond("**ответь на фото**")
            return

        try:
            path = await client.download_media(reply.media, file="meme_input.jpg")
            original = Image.open(path).convert("RGB")

            max_width = 700
            font_path = "/system/fonts/Roboto-Regular.ttf"
            font_size = 40
            font = ImageFont.truetype(font_path, size=font_size)

            w_percent = max_width / original.width
            new_height = int(original.height * w_percent)
            resized = original.resize((max_width, new_height), Image.LANCZOS)

            padding_between = 20
            white_border = 3
            canvas_padding = 30

            img = ImageOps.expand(resized, border=padding_between, fill="black")
            img = ImageOps.expand(img, border=white_border, fill="white")

            max_text_width = img.width - 60
            draw_temp = ImageDraw.Draw(img)

            words = text.split()
            lines = []
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                width = draw_temp.textbbox((0, 0), test_line, font=font)[2]
                if width <= max_text_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)

            text_height = len(lines) * (font_size + 10)
            result = Image.new("RGB", (img.width + canvas_padding * 2, img.height + canvas_padding * 2 + text_height), "black")
            result.paste(img, (canvas_padding, canvas_padding))

            draw = ImageDraw.Draw(result)
            y = canvas_padding + img.height + 10
            for line in lines:
                line_width = draw.textbbox((0, 0), line, font=font)[2]
                x = (result.width - line_width) // 2
                draw.text((x, y), line, font=font, fill="white")
                y += font_size + 10

            output = "meme_output.jpg"
            result.save(output)

            await client.send_file(event.chat_id, output, reply_to=event.id)
            await event.delete()
            os.remove(path)
            os.remove(output)

        except Exception as e:
            await event.respond(f"**ошибка:** `{e}`")