import os
import json
import asyncio
from telethon import TelegramClient

SESSIONS_DIR = "SESSIONS"
CONFIGS_DIR = "configs"
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(CONFIGS_DIR, exist_ok=True)

class UserBot:
    def __init__(self, session_name: str):
        self.session_name = session_name
        self.config = self._load_config()
        self.client = self._create_client()

    def _load_config(self) -> dict:
        path = os.path.join(CONFIGS_DIR, f"{self.session_name}.json")
        with open(path, "r") as f:
            return json.load(f)

    def _create_client(self) -> TelegramClient:
        session_path = os.path.join(SESSIONS_DIR, self.session_name)
        return TelegramClient(session_path, self.config["API_ID"], self.config["API_HASH"])

    async def start(self):
        await self.client.start()

    async def run_until_disconnected(self):
        try:
            await self.start()
            print(f"[{self.session_name}] Бот запущен. Ожидание сообщений...")
            await self.client.run_until_disconnected()
        except (KeyboardInterrupt, SystemExit):
            print(f"[{self.session_name}] Остановка бота по Ctrl+C")
        finally:
            await self.client.disconnect()
            print(f"[{self.session_name}] Соединение закрыто")

    def add_event_handler(self, handler, **kwargs):
        self.client.add_event_handler(handler, **kwargs)

    def on(self, *args, **kwargs):
        return self.client.on(*args, **kwargs)