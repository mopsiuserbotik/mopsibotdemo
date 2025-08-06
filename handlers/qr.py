import io
import re
import os
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode
from telethon import events

def register(client):
    client.add_event_handler(generate_qr, events.NewMessage(pattern=r'^\.qr\s+(.+)'))
    client.add_event_handler(scan_qr, events.NewMessage(pattern=r"\.qrscan"))

async def generate_qr(event):
    text = event.pattern_match.group(1)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    bio = io.BytesIO()
    bio.name = "qrcode.png"
    img.save(bio, format="PNG")
    bio.seek(0)

    await event.client.send_file(event.chat_id, bio)
    await event.delete()

async def scan_qr(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        await event.respond("**ответь на сообщение с QR-кодом**")
        return

    file_path = await reply.download_media()
    if not file_path:
        await event.respond("**не удалось скачать файл**")
        return

    try:
        img = Image.open(file_path)
        decoded = decode(img)
        if not decoded:
            await event.respond("**QR-код не найден или не распознан**")
        else:
            texts = [obj.data.decode('utf-8') for obj in decoded]
            await event.respond("\n".join(texts))
    except Exception as e:
        await event.respond(f"**ошибка при обработке изображения:** {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)