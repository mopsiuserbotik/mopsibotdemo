from telethon import events
from PIL import Image, ImageDraw, ImageFont
import asyncio
import os

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.watermarkf (.+)"))
    async def watermark_photo(event):
        text = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not reply or not reply.media:
            await event.respond("**ответь на фото**")
            return

        input_path = "photo_input.jpg"
        output_path = "photo_output.jpg"

        await event.respond("**обрабатываю фото...**")
        await client.download_media(reply.media, file=input_path)

        try:
            image = Image.open(input_path).convert("RGBA")
            txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
            font_path = "/system/fonts/Roboto-Regular.ttf"
            font = ImageFont.truetype(font_path, size=96)
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (image.width - text_width) // 2 - 30
            y = (image.height - text_height) // 2
            rotated_txt = Image.new("RGBA", txt_layer.size, (255, 255, 255, 0))
            draw_rot = ImageDraw.Draw(rotated_txt)
            draw_rot.text((x, y), text, font=font, fill=(255, 255, 255, 128))
            rotated_txt = rotated_txt.rotate(10, resample=Image.BICUBIC, center=(x + text_width // 2, y + text_height // 2))
            result = Image.alpha_composite(image, rotated_txt).convert("RGB")
            result.save(output_path, "JPEG")
            await client.send_file(event.chat_id, output_path, reply_to=reply.id)
        except Exception as e:
            await event.respond(f"**ошибка обработки фото:** {e}")
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

        await event.delete()

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.watermarkv (.+)"))
    async def watermark_video(event):
        text = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not reply or not reply.media:
            await event.respond("**ответь на видео**")
            return

        input_path = "input_video.mp4"
        output_path = "watermarked_video.mp4"

        await event.respond("**скачиваю видео...**")
        await client.download_media(reply.media, file=input_path)

        drawtext = (
            f"drawtext=text='{text}':"
            "fontcolor=white@0.5:fontsize=40:"
            "box=0:"
            "x='if(lte(mod(t*80\\,(w-text_w)*2),(w-text_w)),mod(t*80\\,(w-text_w)*2),(w-text_w)*2-mod(t*80\\,(w-text_w)*2))':"
            "y='if(lte(mod(t*50\\,(h-text_h)*2),(h-text_h)),mod(t*50\\,(h-text_h)*2),(h-text_h)*2-mod(t*50\\,(h-text_h)*2))'"
        )

        cmd = [
            "ffmpeg", "-i", input_path,
            "-vf", drawtext,
            "-codec:a", "copy",
            "-y", output_path
        ]

        await event.respond("**добавляю прозрачный водяной знак...**")
        process = await asyncio.create_subprocess_exec(*cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await process.communicate()

        if not os.path.exists(output_path):
            await event.respond("**не удалось обработать видео**")
            return

        await client.send_file(event.chat_id, output_path, reply_to=reply.id)

        os.remove(input_path)
        os.remove(output_path)
        await event.delete()