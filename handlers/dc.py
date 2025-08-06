import asyncio
from telethon import events, errors

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.dc$"))
    async def delete_messages_in_all_chats(event):
        await event.respond("**удаляю все свои сообщения в группах...**")
        deleted_total = 0
        chats_checked = 0

        try:
            me = await client.get_me()

            async for dialog in client.iter_dialogs():
                entity = dialog.entity

                if not getattr(entity, 'megagroup', False):
                    continue

                chats_checked += 1
                batch = []

                try:
                    async for msg in client.iter_messages(entity.id, from_user=me.id):
                        batch.append(msg.id)

                        if len(batch) >= 100:
                            try:
                                await client.delete_messages(entity.id, batch)
                                deleted_total += len(batch)
                            except errors.FloodWaitError as e:
                                print(f"[dc] FloodWait: {e.seconds} сек")
                                await asyncio.sleep(e.seconds + 1)
                            except Exception as e:
                                print(f"[dc] ошибка в {entity.id}: {e}")
                            batch.clear()
                            await asyncio.sleep(0.3)

                    if batch:
                        try:
                            await client.delete_messages(entity.id, batch)
                            deleted_total += len(batch)
                        except errors.FloodWaitError as e:
                            await asyncio.sleep(e.seconds + 1)
                            await client.delete_messages(entity.id, batch)
                            deleted_total += len(batch)
                        except Exception as e:
                            print(f"[dc] ошибка в остатке {entity.id}: {e}")

                except Exception as e:
                    print(f"[dc] ошибка чтения сообщений {entity.id}: {e}")
                    continue

            await event.respond(f"**удалено. чатов проверено:** `{chats_checked}`, **сообщений удалено:** `{deleted_total}`")
            await event.delete()

        except Exception as e:
            await event.respond(f"**ошибка выполнения:** `{e}`")