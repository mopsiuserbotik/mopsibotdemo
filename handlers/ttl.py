from telethon import events
from telethon.tl.functions.account import GetAccountTTLRequest

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ttl$"))
    async def ttl_handler(event):
        try:
            ttl = await event.client(GetAccountTTLRequest())
            if ttl.days > 0:
                await event.respond(f"**аккаунт ограничен, удалится через** {ttl.days} **дней**")
            else:
                await event.respond("**аккаунт свободен от ограничений**")
        except:
            await event.respond("**ошибка проверки ограничений**")