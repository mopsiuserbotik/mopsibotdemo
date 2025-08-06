import asyncio
import random
from datetime import datetime
from faker import Faker
from unidecode import unidecode
from telethon import events

locales_map = {
    "Россия": "ru_RU",
    "Украина": "uk_UA",
    "Беларусь": "ru_RU",
    "Казахстан": "ru_RU"
}

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.fakepasta (Украина|Россия|Беларусь|Казахстан) (\d{1,2}) ([МмЖж])"))
    async def handler(event):
        await asyncio.sleep(0.15)
        await event.delete()

        country, age, gender = event.pattern_match.group(1), int(event.pattern_match.group(2)), event.pattern_match.group(3).upper()
        male = gender == "М"

        fake = Faker(locales_map[country])
        Faker.seed()

        full_name = fake.name_male() if male else fake.name_female()
        phone = fake.phone_number()
        email = fake.email()
        address = fake.address().replace("\n", ", ")
        ip = fake.ipv4_public()

        birth_year = datetime.now().year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_date = f"{birth_day:02d}.{birth_month:02d}.{birth_year}"

        translit_name = unidecode(full_name.replace("ё", "е").lower()).split()
        email_base = f"{translit_name[1]}.{translit_name[0]}{random.randint(10,99)}"
        email = f"{email_base}@{random.choice(['gmail.com', 'mail.ru']) if country == 'Россия' else 'gmail.com'}"

        passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
        inn = f"{random.randint(100000000000,999999999999)}"
        snils = f"{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)} {random.randint(10,99)}"
        edu = fake.company()

        if age < 14:
            card = "-"
            driver = "-"
        elif 14 <= age <= 16:
            card = f"{random.randint(4000,4999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
            driver = "-"
        elif age == 18:
            card = f"{random.randint(4000,4999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
            driver = f"{random.randint(1000,9999)} {random.randint(100000,999999)}" if random.choice([True, False]) else "-"
        else:
            card = f"{random.randint(4000,4999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
            driver = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"

        father_name = fake.name_male()
        mother_name = fake.name_female()
        father_passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
        mother_passport = f"{random.randint(1000,9999)} {random.randint(100000,999999)}"
        father_phone = fake.phone_number()
        mother_phone = fake.phone_number()

        msg = f"""ФИО: {full_name}
Дата рождения: {birth_date}
Возраст: {age}
Пол: {"Мужской" if male else "Женский"}
Страна: {country}
Адрес: {address}
Телефон: {phone}
Email: {email}
IP: {ip}
Паспорт: {passport}
ИНН: {inn}
СНИЛС: {snils}
Банковская карта: {card}
Водительские права: {driver}
Образование: {edu}

Родители:
Отец: {father_name}
Паспорт: {father_passport}
Телефон: {father_phone}

Мать: {mother_name}
Паспорт: {mother_passport}
Телефон: {mother_phone}"""

        await event.respond(f"```\n{msg}\n```")