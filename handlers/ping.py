import time
import socket
import os
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"^\.ping$", outgoing=True))
    async def ping_combined(event):
        start = time.time()
        try:
            await client.get_me()
            tg_ping = int((time.time() - start) * 1000)
        except:
            tg_ping = "ошибка"

        try:
            t_start = time.time()
            await client.get_dialogs(limit=1)
            telethon_ping = int((time.time() - t_start) * 1000)
        except:
            telethon_ping = "ошибка"

        try:
            g_start = time.time()
            with socket.create_connection(("google.com", 80), timeout=1) as s:
                pass
            socket_ping = int((time.time() - g_start) * 1000)
        except:
            socket_ping = "недоступен"

        try:
            raw = os.popen("ping -c 1 -W 1 8.8.8.8").read()
            if "time=" in raw:
                icmp = raw.split("time=")[-1].split(" ms")[0]
                icmp_ping = f"{icmp}мс"
            else:
                icmp_ping = "ошибка"
        except:
            icmp_ping = "недоступен"

        result = (
            f"**pong!**\n"
            f"```\n"
            f"пинг телеги     : {tg_ping}мс\n"
            f"пинг telethon   : {telethon_ping}мс\n"
            f"tcp до google   : {socket_ping}мс\n"
            f"icmp (ОС)       : {icmp_ping}\n"
            f"```"
        )
        await event.reply(result)