import os
import aiohttp
import piexif
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from telethon import events
from telethon.tl.types import InputMediaGeoPoint

def convert_to_degrees(value):
    return sum([
        value[0][0] / value[0][1],
        (value[1][0] / value[1][1]) / 60,
        (value[2][0] / value[2][1]) / 3600
    ])

async def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    headers = {"User-Agent": "TelegramMetaBot"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("display_name")
    return None

def extract_exif_info(path):
    try:
        exif = piexif.load(path)
        make = exif.get("0th", {}).get(piexif.ImageIFD.Make, b"").decode(errors="ignore")
        model = exif.get("0th", {}).get(piexif.ImageIFD.Model, b"").decode(errors="ignore")
        date = exif.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
        date = date.decode(errors="ignore") if date else None
        gps = exif.get("GPS", {})
        return make, model, date, gps
    except Exception as e:
        return None, None, None, f"ошибка piexif: {e}"

def extract_tech_info(path):
    try:
        parser = createParser(path)
        if parser:
            with parser:
                metadata = extractMetadata(parser)
            if metadata:
                return metadata.exportPlaintext()
    except:
        return ["hachoir: ошибка при чтении метаданных"]
    return []

def gps_info(gps):
    try:
        lat = convert_to_degrees(gps[piexif.GPSIFD.GPSLatitude])
        if gps[piexif.GPSIFD.GPSLatitudeRef] != b'N':
            lat = -lat
        lon = convert_to_degrees(gps[piexif.GPSIFD.GPSLongitude])
        if gps[piexif.GPSIFD.GPSLongitudeRef] != b'E':
            lon = -lon
        return lat, lon
    except Exception as e:
        return f"ошибка при извлечении GPS: {e}"

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.meta$', outgoing=True))
    async def meta_handler(event):
        if not event.is_reply:
            return await event.reply("**используй в ответ на медиафайл**")

        reply = await event.get_reply_message()
        if not reply.file:
            return await event.reply("**это не файл.**")

        path = await reply.download_media(file="./meta_tmp.jpg")
        out = f"**метаданные файла `{os.path.basename(path)}`:**\n\n"

        tech = extract_tech_info(path)
        if tech:
            out += "**технические характеристики:**\n" + '\n'.join(f"• {line}" for line in tech) + '\n'

        make, model, date, gps = extract_exif_info(path)
        if any([make, model, date]):
            out += "\n**EXIF-данные:**\n"
            if make: out += f"• производитель: {make}\n"
            if model: out += f"• модель: {model}\n"
            if date: out += f"• дата съёмки: {date}\n"

        location = None
        if isinstance(gps, dict) and gps:
            out += f"\n**RAW GPS:** {gps}\n"
            coords = gps_info(gps)
            if isinstance(coords, tuple):
                lat, lon = coords
                out += f"• координаты: {lat:.6f}, {lon:.6f}\n"
                address = await reverse_geocode(lat, lon)
                if address:
                    out += f"• адрес: {address}\n"
                location = InputMediaGeoPoint(lat=lat, long=lon)
            else:
                out += f"• {coords}\n"
        elif isinstance(gps, str):
            out += f"\n**{gps}**\n"

        await event.reply(out[:4096])
        if location:
            await event.client.send_message(event.chat_id, location)

        os.remove(path)