import os
import json
import time
import re
import random
from datetime import datetime
from art import text2art
from telethon import TelegramClient

ACCOUNTS_FILE = "accounts.json"
SESSIONS_DIR = "SESSIONS"
CONFIGS_DIR = "configs"

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
YELLOW = "\033[93m"
RESET = "\033[0m"
CLEAR = "cls" if os.name == "nt" else "clear"

ascii_styles = [
    "tarty1", "banner3-D", "cybermedium", "soft", "ghost", "big", "chunky", "epic", "weird",
    "graffiti", "3d", "cyberlarge", "avatar", "doom", "slscript", "amcrazor", "twopoint", "xhelvi",
    "sub-zero", "fuzzy", "amcslash", "bulbhead", "amcrazo2", "charact1", "contessa", "drpepper",
    "nancyj", "pepper", "puffy", "rectangles", "smkeyboard", "starwars", "stampatello", "thick",
    "twisted", "whimsy"
]

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(CONFIGS_DIR, exist_ok=True)

class AccountsManager:
    def __init__(self):
        self.accounts = self._load_accounts()

    def _load_accounts(self):
        if not os.path.exists(ACCOUNTS_FILE):
            return []
        try:
            with open(ACCOUNTS_FILE, "r") as f:
                return json.load(f)
        except:
            return []

    def _save_accounts(self):
        with open(ACCOUNTS_FILE, "w") as f:
            json.dump(self.accounts, f, indent=4)

    def _clear_screen(self):
        os.system(CLEAR)

    def _type_print(self, text, color=None, delay=0.003):
        if color:
            text = f"{color}{text}{RESET}"
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()

    def _show_banner(self):
        style = random.choice(ascii_styles)
        banner = text2art("MOPSI USERBOT", font=style)
        print(banner.rstrip())
        lines = banner.rstrip().split('\n')
        footer = f"[{style}]"
        pad = max(0, max(len(line) for line in lines) - len(footer))
        print(" " * pad + footer)

    def _is_valid_name(self, name):
        return bool(re.fullmatch(r"[A-Za-z0-9_-]{3,20}", name))

    def _delete_session_files(self, session_name):
        base = os.path.join(SESSIONS_DIR, session_name)
        for ext in [".session", ".session-journal", ".session-shm"]:
            f = base + ext
            if os.path.exists(f):
                os.remove(f)

    def _delete_config(self, session_name):
        config_path = os.path.join(CONFIGS_DIR, f"{session_name}.json")
        if os.path.exists(config_path):
            os.remove(config_path)

    def _input(self, prompt, color=BLUE):
        return input(f"{color}{prompt}{RESET}")

    async def add_account(self):
        name = self._input("Введите имя сессии: ").strip()
        if not self._is_valid_name(name):
            self._type_print("Недопустимое имя сессии.", RED)
            return
        if any(a["session_name"] == name for a in self.accounts):
            self._type_print("Такое имя уже используется.", RED)
            return

        try:
            api_id_str = self._input("API ID: ").strip()
            if not api_id_str.isdigit():
                self._type_print("API ID должен быть числом.", RED)
                return
            api_id = int(api_id_str)
            api_hash = self._input("API HASH: ").strip()
            phone = self._input("Номер телефона (включая +): ").strip()
            password = self._input("Пароль от облака (если есть, иначе Enter): ").strip() or None
        except Exception:
            self._type_print("Ошибка ввода данных.", RED)
            return

        path = os.path.join(SESSIONS_DIR, name)
        client = TelegramClient(path, api_id, api_hash)

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = self._input("Код из Telegram: ").strip()
                try:
                    await client.sign_in(phone, code, password=password)
                except Exception:
                    self._type_print("Ошибка входа: неверный код или пароль.", RED)
                    return

            me = await client.get_me()
            self.accounts.append({
                "session_name": name,
                "phone": phone,
                "username": me.username or "",
                "first_name": me.first_name or "",
                "last_used": time.time()
            })
            self._save_accounts()

            config_path = os.path.join(CONFIGS_DIR, f"{name}.json")
            with open(config_path, "w") as f:
                json.dump({"API_ID": api_id, "API_HASH": api_hash}, f, indent=4)

            self._type_print(f"Аккаунт @{me.username or name} успешно добавлен.", GREEN)
        except Exception as e:
            self._type_print(f"Ошибка подключения или авторизации: {e}", RED)
            self._delete_session_files(name)
            self._delete_config(name)
        finally:
            await client.disconnect()

    def list_accounts(self):
        if not self.accounts:
            self._type_print("Нет добавленных аккаунтов.", RED)
            return
        for i, acc in enumerate(self.accounts, 1):
            stamp = datetime.fromtimestamp(acc.get("last_used", 0)).strftime("%Y-%m-%d %H:%M")
            line = f"{i}. {BLUE}{acc['phone']}{RESET} | {YELLOW}{acc['session_name']}{RESET} | Последний запуск: {stamp}"
            self._type_print(line, GREEN)

    def delete_account(self):
        if not self.accounts:
            self._type_print("Список аккаунтов пуст.", RED)
            return
        self.list_accounts()
        try:
            idx_str = self._input("Номер аккаунта для удаления: ", GREEN).strip()
            if not idx_str.isdigit():
                self._type_print("Неверный ввод.", RED)
                return
            idx = int(idx_str)
            if 1 <= idx <= len(self.accounts):
                acc = self.accounts.pop(idx - 1)
                self._save_accounts()
                self._delete_session_files(acc["session_name"])
                self._delete_config(acc["session_name"])
                self._type_print("Аккаунт удалён.", GREEN)
            else:
                self._type_print("Неверный номер.", RED)
        except Exception:
            self._type_print("Ошибка ввода.", RED)

    def select_account(self):
        if not self.accounts:
            self._type_print("Нет аккаунтов.", RED)
            return None
        self.list_accounts()
        try:
            idx_str = self._input("Номер аккаунта для запуска: ", GREEN).strip()
            if not idx_str.isdigit():
                self._type_print("Неверный ввод.", RED)
                return None
            idx = int(idx_str)
            if 1 <= idx <= len(self.accounts):
                acc = self.accounts[idx - 1]
                acc["last_used"] = time.time()
                self._save_accounts()
                self._type_print(f"Выбран аккаунт: {BLUE}{acc['session_name']}{RESET}", GREEN)
                return acc["session_name"]
            else:
                self._type_print("Неверный номер.", RED)
        except Exception:
            self._type_print("Ошибка ввода.", RED)
        return None

    async def run_menu(self):
        while True:
            self._clear_screen()
            self._show_banner()

            self._type_print("\n1. Добавить аккаунт\n2. Список аккаунтов\n3. Удалить аккаунт\n4. Запустить аккаунт\n5. Выход", GREEN)
            print(f"\n{' ' * 20}{PURPLE}DEV: @mopsiuser & ChatGPT edition){RESET}")
            print(f"{' ' * 20}{PURPLE}TGK: @MopsiProject{RESET}")

            try:
                choice = input("Ваш выбор: ").strip()
                if choice == "1":
                    await self.add_account()
                elif choice == "2":
                    self.list_accounts()
                elif choice == "3":
                    self.delete_account()
                elif choice == "4":
                    session = self.select_account()
                    if session:
                        return session
                elif choice == "5":
                    exit(0)
                else:
                    self._type_print("Неверный выбор.", RED)
                input("\nНажмите Enter для продолжения...")
            except KeyboardInterrupt:
                self._type_print("\nВыход.", RED)
                break