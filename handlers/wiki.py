from telethon import events
from langdetect import detect
import wikipedia
import asyncio

WIKI_LANGS = ["ru", "uk", "en"]  

def get_best_lang(query):
    try:
        lang = detect(query)
        return lang if lang in WIKI_LANGS else "ru"
    except:
        return "ru"

def register(client):
    @client.on(events.NewMessage(pattern=r'^\.wiki (.+)'))
    async def wiki(event):
        query = event.pattern_match.group(1).strip()
        msg = await event.respond("**ищу в Википедии...**")
        await asyncio.sleep(0.05)

        try:
            wikipedia.set_lang(get_best_lang(query))
            summary = wikipedia.summary(query, sentences=3)
            if len(summary) > 4000:
                summary = summary[:3990] + "..."
            await msg.edit(f"**{query.capitalize()}**:\n{summary}")

        except wikipedia.exceptions.DisambiguationError as e:
            options = []
            for opt in e.options[:5]:
                try:
                    s = wikipedia.summary(opt, sentences=1)
                    options.append(f"• **{opt}** — {s}")
                except:
                    options.append(f"• **{opt}** — (недоступно)")
            result = f"**несколько вариантов для** `{query}`:\n\n" + "\n".join(options)
            await msg.edit(result[:4000])

        except wikipedia.exceptions.PageError:
            await msg.edit("**страница не найдена.**")

        except Exception as e:
            await msg.edit(f"**ошибка:** {e}")


    @client.on(events.NewMessage(pattern=r'^\.wikifull (.+)'))
    async def wikifull(event):
        query = event.pattern_match.group(1).strip()
        msg = await event.respond("**получаю полную статью...**")
        await asyncio.sleep(0.05)

        try:
            wikipedia.set_lang(get_best_lang(query))
            content = wikipedia.page(query).content

            chunks = [content[i:i+4000] for i in range(0, len(content), 4000)]
            await msg.edit(f"**{query.capitalize()}**:\n{chunks[0]}")
            for chunk in chunks[1:]:
                await event.respond(chunk)

        except wikipedia.exceptions.DisambiguationError as e:
            opts = "\n".join(f"• {o}" for o in e.options[:10])
            await msg.edit(f"**несколько вариантов для** `{query}`:\n\n{opts[:4000]}")

        except wikipedia.exceptions.PageError:
            await msg.edit("**страница не найдена.**")

        except Exception as e:
            await msg.edit(f"**ошибка:** {e}")