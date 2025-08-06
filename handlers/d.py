from telethon import events
import asyncio

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.d(?: (\d+))?$'))
    async def delete_reply_and_command(event):

        if not event.is_reply:
            return await event.respond('**ответь командой `.d` на сообщение, которое хочешь удалить**')

        try:
            await event.delete()
            reply = await event.get_reply_message()

            if reply:
                can_delete = (
                    reply.out or
                    (await event.client.get_permissions(event.chat_id, 'me')).is_admin
                )

                if can_delete:
                    await reply.delete()
                else:
                    await event.respond('**недостаточно прав для удаления чужого сообщения**')

        except Exception as e:
            await event.respond(f'**ошибка при удалении:** {e}')