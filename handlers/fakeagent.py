import random
from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.fakeagent(?: (\w+))?"))
    async def fake_user_agent(event):
        await event.delete()
        arg = (event.pattern_match.group(1) or "").lower()

        platforms = {
            "windows": [
                "Windows NT 10.0; Win64; x64",
                "Windows NT 10.0; WOW64",
                "Windows NT 6.1; Win64; x64",
            ],
            "linux": [
                "X11; Linux x86_64",
                "X11; Ubuntu; Linux x86_64",
                "X11; Fedora; Linux x86_64"
            ],
            "macos": [
                "Macintosh; Intel Mac OS X 10_15_7",
                "Macintosh; Intel Mac OS X 11_6",
                "Macintosh; Intel Mac OS X 12_0"
            ],
            "android": [
                "Linux; Android 11; Infinix X6816D",
                "Linux; Android 12; Redmi Note 10",
                "Linux; Android 13; Samsung Galaxy S21"
            ],
            "ios": [
                "iPhone; CPU iPhone OS 14_6 like Mac OS X",
                "iPhone; CPU iPhone OS 15_4 like Mac OS X",
                "iPad; CPU OS 14_0 like Mac OS X"
            ]
        }

        browsers = [
            ("Chrome", lambda: f"{random.randint(100, 125)}.0.{random.randint(1000,9999)}.{random.randint(0,150)}"),
            ("Firefox", lambda: f"{random.randint(90, 118)}.0"),
            ("Safari", lambda: f"{random.randint(604, 615)}.1.{random.randint(1,9)}"),
            ("Edge", lambda: f"{random.randint(100, 115)}.0.{random.randint(1000,9999)}.{random.randint(0,150)}"),
            ("Opera", lambda: f"{random.randint(70, 95)}.0.{random.randint(1000,9999)}.{random.randint(0,150)}")
        ]

        platform_group = platforms.get(arg, random.choice(list(platforms.values())))
        platform = random.choice(platform_group)
        browser, version_fn = random.choice(browsers)
        version = version_fn()

        if browser == "Safari":
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
        elif browser == "Firefox":
            ua = f"Mozilla/5.0 ({platform}; rv:{version}) Gecko/20100101 Firefox/{version}"
        elif browser == "Chrome":
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        elif browser == "Edge":
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 Edg/{version}"
        elif browser == "Opera":
            ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36 OPR/{version}"
        else:
            ua = f"Mozilla/5.0 ({platform})"

        await event.respond(f"```\n{ua}\n```")