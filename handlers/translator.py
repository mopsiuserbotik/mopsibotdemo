from telethon import events
from googletrans import Translator

translator = Translator()
auto_translate_chats = {}
chat_lang = {}

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.t(?: (.+))?$'))
    async def translate_cmd(event):
        chat_id = event.chat_id
        param = event.pattern_match.group(1)

        if param is None:
            await event.respond("**использование:**\n"
                                "`.t ru/en/uk` — перевести сообщение и задать язык\n"
                                "`.t on` — включить авто-перевод\n"
                                "`.t off` — выключить авто-перевод")
            return

        param = param.lower()

        if param in ["ru", "uk", "en"]:
            chat_lang[chat_id] = param
            reply = await event.get_reply_message()
            if not reply or not reply.text:
                await event.respond("**язык задан, ответь на текстовое сообщение для перевода**")
                return
            try:
                result = translator.translate(reply.text, dest=param)
                if result.src != param:
                    await event.respond(f"**перевод [{result.src} -> {param}]:**\n{result.text}")
                else:
                    await event.respond("**исходный язык совпадает с целевым, перевод не требуется.**")
            except Exception as e:
                await event.respond(f"**ошибка перевода:** {e}")

        elif param == "on":
            if chat_id not in chat_lang:
                await event.respond("**сначала задай язык перевода командой `.t ru/en/uk`**")
                return
            auto_translate_chats[chat_id] = True
            await event.respond(f"**авто-перевод включён на язык: {chat_lang[chat_id]}**")

        elif param == "off":
            if chat_id in auto_translate_chats:
                del auto_translate_chats[chat_id]
            await event.respond("**авто-перевод выключен**")

        else:
            await event.respond("**неверный параметр. Используй `.t ru/en/uk`, `.t on` или `.t off`.**")

    @client.on(events.NewMessage(incoming=True))
    async def auto_translate(event):
        chat_id = event.chat_id
        if chat_id in auto_translate_chats and not event.out:
            lang = chat_lang.get(chat_id)
            if not lang or not event.message.text:
                return
            try:
                result = translator.translate(event.message.text, dest=lang)
                if result.src != lang and result.text != event.message.text:
                    await event.respond(f"**авто-перевод [{result.src} -> {lang}]:**\n{result.text}")
            except:
                pass