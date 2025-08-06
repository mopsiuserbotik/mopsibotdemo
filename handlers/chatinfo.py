from telethon import events
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio

def register(client):
    @client.on(events.NewMessage(pattern=r"\.chatinfo$", outgoing=True))
    async def handler(event):
        await asyncio.sleep(0.15)
        try:
            entity = await event.get_chat()
            chat = await event.get_input_chat()

            chat_id = entity.id
            title = entity.title or "—"
            username = f"@{entity.username}" if getattr(entity, 'username', None) else "—"
            is_group = getattr(entity, 'megagroup', False)
            is_channel = getattr(entity, 'broadcast', False)
            chat_type = "Супергруппа" if is_group else "Канал" if is_channel else "Группа"

            members = await client.get_participants(chat)
            member_count = len(members)

            admin_list = []
            async for user in client.iter_participants(chat, filter=ChannelParticipantsSearch('')):
                try:
                    part = await client(GetParticipantRequest(chat, user.id))
                    if getattr(part.participant, 'admin_rights', None):
                        name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "—"
                        admin_list.append(f"{name} (`{user.id}`)")
                except:
                    continue

            message_count = 0
            async for _ in client.iter_messages(chat):
                message_count += 1

            info = f"**Информация о чате:**\n\n"
            info += f"**Название:** {title}\n"
            info += f"**Тип:** {chat_type}\n"
            info += f"**ID:** `{chat_id}`\n"
            info += f"**Юзернейм:** {username}\n"
            info += f"**Участников:** {member_count}\n"
            info += f"**Админов:** {len(admin_list)}\n"
            info += "\n".join([f"• {a}" for a in admin_list[:10]])
            info += f"\n**Сообщений:** {message_count}"

            if hasattr(entity, 'date'):
                info += f"\n**Дата создания:** {entity.date.strftime('%d.%m.%Y %H:%M:%S')}"

            await event.respond(info)

        except Exception as e:
            await event.respond(f"**Ошибка получения информации о чате:** {e}")