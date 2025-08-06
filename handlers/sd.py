import re
import os
import tempfile
import aiohttp
from bs4 import BeautifulSoup
from telethon import events

def register(client):
    @client.on(events.NewMessage(pattern=r"\.sd(?:\s+(.+))?"))
    async def sd_clean_html(event):
        url = event.pattern_match.group(1)

        if not url and event.is_reply:
            reply = await event.get_reply_message()
            words = reply.message.split()
            url = next((w for w in words if "." in w or w.startswith("http")), None)

        if not url:
            await event.reply("**ссылка не найдена**")
            return

        url = url.strip()
        if not re.match(r"^https?://", url):
            url = "https://" + url

        try:
            async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
                async with session.get(url, timeout=15) as resp:
                    content_type = resp.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        await event.reply(f"**не HTML-страница**\n`Content-Type: {content_type}`")
                        return

                    raw_html = await resp.text()
                    soup = BeautifulSoup(raw_html, "html.parser")

                    for tag in soup(["script", "style", "iframe", "noscript", "svg"]):
                        tag.decompose()

                    ad_classes = ["ad", "ads", "adsbygoogle", "sponsored", "banner", "promo"]
                    for tag in soup.find_all(True, {"class": re.compile("|".join(ad_classes))}):
                        tag.decompose()
                    for tag in soup.find_all(True, {"id": re.compile("|".join(ad_classes))}):
                        tag.decompose()

                    pretty_html = soup.prettify()

                    with tempfile.NamedTemporaryFile("w+", suffix=".html", delete=False, encoding="utf-8") as tmp:
                        tmp.write(pretty_html)
                        tmp_path = tmp.name

            await event.reply(file=tmp_path)
            os.remove(tmp_path)

        except Exception as e:
            await event.reply(f"**ошибка запроса**\n`{str(e)}`")