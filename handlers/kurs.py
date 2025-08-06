import requests
from telethon import events

def register(client):
    CURRENCY_MAP = {
        "bts": "bitcoin",
        "btc": "bitcoin",
        "ton": "ton",
        "usdt": "tether",
        "usd": "usd",
        "uah": "uah",
        "rub": "rub",
        "eur": "eur",
    }

    CRYPTO_IDS = {"bitcoin", "tether"}

    @client.on(events.NewMessage(pattern=r"\.kurs\s+(\w+)(?:\s+([\d.,]+))?"))
    async def kurs_handler(event):
        code = event.pattern_match.group(1).lower()
        amount_str = event.pattern_match.group(2) or "1"

        try:
            amount = float(amount_str.replace(',', '.'))
        except ValueError:
            await event.respond("**Неверное значение суммы**")
            return

        if code not in CURRENCY_MAP:
            await event.respond(f"**Неизвестный код валюты:** `{code}`")
            return

        mapped = CURRENCY_MAP[code]

        if mapped == "ton":
            try:
                resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT", timeout=10).json()
                price = float(resp["price"]) * amount
                await event.respond(f"**TON (TON/USDT)**\n{amount} TON = {price:,.4f} USD")
            except Exception as e:
                await event.respond(f"**Не удалось получить курс TON:** {e}")
            return

        if mapped in CRYPTO_IDS:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": mapped, "vs_currencies": "usd,eur,rub,uah"}
            headers = {"User-Agent": "Mozilla/5.0"}

            try:
                resp = requests.get(url, params=params, headers=headers, timeout=10).json()
                data = resp.get(mapped)
                if not data:
                    await event.respond(f"**CoinGecko не вернул данные для** `{mapped}`.")
                    return

                lines = [f"**{code.upper()} (криптовалюта)** — {amount} шт."]
                for cur, val in data.items():
                    lines.append(f"{cur.upper()}: {val * amount:,.4f}")

                await event.respond("\n".join(lines))
            except Exception as e:
                await event.respond(f"**Ошибка при получении данных:** {e}")
            return

        url = f"https://open.er-api.com/v6/latest/{code.upper()}"
        try:
            resp = requests.get(url, timeout=10).json()
            if resp.get("result") != "success" or "rates" not in resp:
                await event.respond("**Ошибка от API валют**")
                return

            rates = resp["rates"]
            targets = ["USD", "EUR", "RUB", "UAH"]
            lines = [f"**{code.upper()} (фиат)** — {amount} шт."]
            for cur in targets:
                if cur in rates:
                    lines.append(f"{amount} {code.upper()} = {rates[cur] * amount:,.4f} {cur}")

            await event.respond("\n".join(lines))
        except Exception as e:
            await event.respond(f"**Ошибка при запросе валют:** {e}")