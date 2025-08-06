from telethon import events
import asyncio
from telethon.tl.types import InputMediaDice

best_values = {
    "darts": 6,
    "footb": 4,
    "basket": 4,
    "boul": 6,
    "slots": 1
}

emojis = {
    "darts": "🎯",
    "footb": "⚽",
    "basket": "🏀",
    "boul": "🎳",
    "slots": "🎰"
}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.(darts|footb|basket|boul|slots)$"))
    async def rigged_game(event):
        game = event.pattern_match.group(1)
        emoji = emojis[game]
        target = best_values[game]

        await asyncio.sleep(0)
        await client.delete_messages(event.chat_id, event.id)

        while True:
            try:
                msg = await client.send_message(event.chat_id, file=InputMediaDice(emoji))
                if game == "slots":
                    if msg.media.value in [1, 22, 43, 64]:
                        break
                elif msg.media.value == target:
                    break
                await client.delete_messages(event.chat_id, msg.id)
            except Exception as e:
                print(f"[{game.upper()}] **ошибка**: {e}")
                break

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.dice (\d)$"))
    async def rigged_dice_fast(event):
        try:
            target = int(event.pattern_match.group(1))
            if not 1 <= target <= 6:
                await event.respond("**введи число от 1 до 6**.")
                return

            await asyncio.sleep(0)
            await client.delete_messages(event.chat_id, event.id)

            while True:
                try:
                    msg = await client.send_message(event.chat_id, file=InputMediaDice("🎲"))
                    if msg.media.value == target:
                        break
                    await client.delete_messages(event.chat_id, msg.id)
                except Exception as e:
                    print(f"[DICE] **ошибка**: {e}")
                    break
        except Exception as e:
            print(f"[INPUT] **ошибка аргумента**: {e}")