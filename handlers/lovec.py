import re
from telethon import events

def register(client):
    state = {"enabled": False}  

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.lovec (on|off)$"))
    async def toggle_lovec(event):
        state["enabled"] = event.pattern_match.group(1) == "on"
        print(f"[LOVEC] Состояние: {'ON' if state['enabled'] else 'OFF'}")
        await event.respond(f"**ловец чеков {'включён' if state['enabled'] else 'выключен'}**")
        await event.delete()

    @client.on(events.NewMessage(incoming=True))
    async def lovec_catcher(event):
        if not state["enabled"] or not event.message:
            return

        try:
            sender = await event.get_sender()
            chat_name = getattr(sender, 'username', None) or getattr(sender, 'title', None) or str(event.chat_id)
            text = event.raw_text or ""
            urls = []

            def log(bot, code):
                print(f"[LOVEC] {bot}: чек `{code}` от {chat_name}")

            def send(bot, code):
                client.loop.create_task(client.send_message(bot, f"/start {code}"))

            def handle_check(bot, pattern, limit, source):
                match = re.search(pattern, source)
                if match:
                    code = match.group(0)[:limit]
                    log(bot, code)
                    send(bot, code)

            handle_check("CryptoBot", r"CQ\w{8,}", 12, text)
            handle_check("CryptoBot", r"start=CQ\w{8,}", 12, text)
            handle_check("wallet", r"C-\w{8,}", 12, text)
            handle_check("tonRocketBot", r"t_\w{10,}", 17, text)
            handle_check("tonRocketBot", r"mc_\w{10,}", 18, text)
            handle_check("tonRocketBot", r"mci_\w{10,}", 19, text)

            if "http://t.me/RandomTGbot?start=" in text:
                token = text.split("start=")[-1].strip()
                log("RandomTGbot", token)
                await client.send_message("RandomTGbot", f"/start {token}")

            if event.message.buttons:
                for row in event.message.buttons:
                    for button in row:
                        if hasattr(button, 'url') and button.url:
                            urls.append(button.url)

            for url in urls:
                handle_check("CryptoBot", r"CQ\w{8,}", 12, url)
                handle_check("CryptoBot", r"start=CQ\w{8,}", 12, url)
                handle_check("wallet", r"C-\w{8,}", 12, url)
                handle_check("tonRocketBot", r"t_\w{10,}", 17, url)
                handle_check("tonRocketBot", r"mc_\w{10,}", 18, url)
                handle_check("tonRocketBot", r"mci_\w{10,}", 19, url)

        except Exception as e:
            print(f"[LOVEC][ERROR] {e}")