import asyncio
import base64
import marshal
import urllib.parse
from telethon import events

rot13_table = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
)

supported_encodings = [
    "bs4", "utf8", "hex", "url", "bin", "rot13",
    "caesar", "xor", "base32", "base85", "marshal"
]

def split_text(text, max_len=4000):
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

def caesar_cipher(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            if 'А' <= char <= 'я':
                start = ord('А')
                result.append(chr((ord(char) - start + shift) % 32 + start))
            elif 'A' <= char <= 'Z' or 'a' <= char <= 'z':
                start = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - start + shift) % 26 + start))
        else:
            result.append(char)
    return ''.join(result)

def xor_cipher(data, key):
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))

def register(client):
    @client.on(events.NewMessage(outgoing=True))
    async def mega_coder(event):
        await asyncio.sleep(0.15)
        text = event.raw_text
        if not (text.startswith(".code") or text.startswith(".decode")):
            return

        parts = text.split(None, 2)
        if text.strip() in [".code", ".decode"]:
            await event.respond("**использование:** `.code <формат> <текст>` или `.decode <формат?> <текст>`\n**форматы:** " + ", ".join(supported_encodings))
            return

        if len(parts) < 2:
            await event.respond("**укажи формат и текст**")
            return

        action = parts[0][1:]
        encoding = None
        message = ""

        if len(parts) == 2:
            message = parts[1]
        else:
            encoding = parts[1].lower()
            message = parts[2]

        message = message.strip('\n\r')

        if len(message) > 10000:
            await event.respond("**текст слишком длинный**")
            return

        if action == "code":
            if encoding not in supported_encodings:
                await event.respond("**неподдерживаемый формат:** `" + encoding + "`\n**варианты:** " + ", ".join(supported_encodings))
                return

            try:
                if encoding == "bs4":
                    result = base64.b64encode(message.encode()).decode()
                elif encoding == "utf8":
                    result = "".join(f"\\x{b:02x}" for b in message.encode())
                elif encoding == "hex":
                    result = message.encode().hex()
                elif encoding == "url":
                    result = urllib.parse.quote(message)
                elif encoding == "bin":
                    result = ' '.join(format(ord(c), '08b') for c in message)
                elif encoding == "rot13":
                    result = message.translate(rot13_table)
                elif encoding == "caesar":
                    if ":" in message:
                        msg, shift = message.rsplit(":", 1)
                        shift = int(shift.strip())
                    else:
                        msg = message
                        shift = 3
                    result = caesar_cipher(msg, shift)
                elif encoding == "xor":
                    if ":" not in message:
                        await event.respond("**для XOR укажи ключ после `:`. Пример:** `.code xor текст :ключ`")
                        return
                    msg, key = message.rsplit(":", 1)
                    result = xor_cipher(msg.strip(), key.strip())
                elif encoding == "base32":
                    result = base64.b32encode(message.encode()).decode()
                elif encoding == "base85":
                    result = base64.b85encode(message.encode()).decode()
                elif encoding == "marshal":
                    result = base64.b64encode(marshal.dumps(message)).decode()

                for chunk in split_text(result):
                    if len(chunk) < 100:
                        await event.respond(f"`{chunk}`")
                    else:
                        await event.respond(f"```\n{chunk}\n```")
            except Exception as e:
                await event.respond(f"**ошибка кодирования:** {e}")
            return

        if action == "decode":
            raw = message.strip()
            decoded = None

            try:
                if encoding:
                    if encoding == "utf8":
                        raw_bytes = bytes(raw.encode("utf-8").decode("unicode_escape"), "latin1")
                        decoded = raw_bytes.decode("utf-8")
                    elif encoding == "bs4":
                        decoded = base64.b64decode(raw).decode()
                    elif encoding == "hex":
                        decoded = bytes.fromhex(raw).decode()
                    elif encoding == "url":
                        decoded = urllib.parse.unquote(raw)
                    elif encoding == "bin":
                        bits = raw.replace(" ", "")
                        decoded = ''.join([chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)])
                    elif encoding == "rot13":
                        decoded = raw.translate(rot13_table)
                    elif encoding == "caesar":
                        if ":" in raw:
                            msg, shift = raw.rsplit(":", 1)
                            shift = int(shift.strip())
                        else:
                            msg = raw
                            shift = 3
                        decoded = caesar_cipher(msg, -shift)
                    elif encoding == "xor":
                        msg, key = raw.rsplit(":", 1)
                        decoded = xor_cipher(msg.strip(), key.strip())
                    elif encoding == "base32":
                        decoded = base64.b32decode(raw).decode()
                    elif encoding == "base85":
                        decoded = base64.b85decode(raw).decode()
                    elif encoding == "marshal":
                        decoded = marshal.loads(base64.b64decode(raw))
                else:
                    try:
                        raw_bytes = bytes(raw.encode("utf-8").decode("unicode_escape"), "latin1")
                        decoded = raw_bytes.decode("utf-8")
                    except:
                        pass
                    if not decoded:
                        try:
                            decoded = base64.b64decode(raw).decode()
                        except:
                            pass
                    if not decoded:
                        try:
                            temp = urllib.parse.unquote(raw)
                            if temp != raw:
                                decoded = temp
                        except:
                            pass
                    if not decoded:
                        try:
                            decoded = bytes.fromhex(raw).decode()
                        except:
                            pass
                    if not decoded and all(c in "01 " for c in raw):
                        try:
                            bits = raw.replace(" ", "")
                            decoded = ''.join([chr(int(bits[i:i+8], 2)) for i in range(0, len(bits), 8)])
                        except:
                            pass
                    if not decoded:
                        try:
                            rot = raw.translate(rot13_table)
                            if rot != raw:
                                decoded = rot
                        except:
                            pass
                    if not decoded:
                        try:
                            decoded = caesar_cipher(raw, -3)
                        except:
                            pass
                    if not decoded and ":" in raw:
                        try:
                            msg, key = raw.rsplit(":", 1)
                            decoded = xor_cipher(msg.strip(), key.strip())
                        except:
                            pass
                    if not decoded:
                        try:
                            decoded = base64.b32decode(raw).decode()
                        except:
                            pass
                    if not decoded:
                        try:
                            decoded = base64.b85decode(raw).decode()
                        except:
                            pass
                    if not decoded:
                        try:
                            decoded = marshal.loads(base64.b64decode(raw))
                        except:
                            pass

                if not decoded:
                    await event.respond("**не удалось расшифровать. проверь формат или данные.**")
                    return

                for chunk in split_text(str(decoded)):
                    if len(chunk) < 100:
                        await event.respond(f"`{chunk}`")
                    else:
                        await event.respond(f"```\n{chunk}\n```")
            except Exception as e:
                await event.respond(f"**ошибка расшифровки:** {e}")