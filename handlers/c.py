from telethon import events

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.c$"))
    async def command_list(event):
        text = """**КОМАНДЫ:**
```text
💉.ai — ИИ
.ar on/off — авто-реакция
.ascii N — ascii-арт
.asciif — ascii-арт фото
.audio — извлечь аудио
💉.autodel -/all on/off — удалять прошлое смс
.auto -/all on/off — автоответ
💉.autoai on/off — автоответ ИИ
.autoban/automute clean/on/off — фильтр
.bazz -/off — дразнилка
.bassboost режим N — басс
.bin — инфо бин-код
.bw — ч-б фильтр
.chatinfo — инфо чата
.clean — удалить все смс
💉.clone — скопировать профиль
.code/decode — шифр/дешифр
.d — удалить смс
.dc — удалить свои смс в группах
.dmu - удалить смс юзера
.del up/down — удалить смс выше/ниже
.delete N — удалить последних смс
.dice N/boul/basket/footb/darts/slots — игры до победы
💉.dl — удалить свои смс
.fakepasta страна возраст м/ж — фейк паста
.fakeagent платформа — фейк юзерагент
.of/rm/sf путь — отправить/удалить/сохранить
.forward юзернейм N — переслать
.fp N — установить аватарку
.gif — сделать гиф
.gitclone — скачать гит
.grab юзернейм тип — переслать материалы
.h — бан/мут список
.id — айди юзера
.info — инфо юзера
.inversion — инверсия фото
.ip — инфо по айпи
.join — вступить
💉.k айди N on/off — авто-коммент
💉.kill/banall — кикнуть/забанить всех
.kurs btc/usdt/ton/uah/rub/usd/eur N — курс валют
.lock on/off — закрыть чат
💉.lovec on/off — ловец чеков
.ls путь — список файлов
.mem — субтитры
.meta — мета-дата
.mirror айди айди on/off — зеркалить чат
💉.mnd on/off — удалять сообщения после команды
.mute/unmute/ban/unban/kick — админка
.mockreply — автоответ юзеру
.mv — переименовать
.o v/g — кружок/голосовое
💉.p айди on/off — ловец приваток
.panic — сброс профиля
.pch — парсинг чата
.pin/unpin — закрепить/открепить
.ping — пинг
.name/bio/username — редактор профиля
.proxy N — генератор прокси
.qr/qrscan — QR-код
💉.rai -/all айди on/off — автоответ ИИ группы
.random N N — рандом число
💉.read all/on/off — авто-читатель
💉.rs айди on/off — рассылка
.sb — спам-блок
.sc on/off — копировать юзера
.sd — фронтед сайта
.send — отправить 
.sendloop — бесконечно отправлять
.sessions — сессии
.siteinfo — инфо сайта
.sks/skp/skc — счетчик старт/пауза/стоп
.sm on/off — все в избранное
.smsall — разослать всем в лс
.spam N — спам
.speedup/slowed N -/reverb — музыка
.stateme — статистика профиля
.sticker — стикер
.stripekey — инфо страйп-ключа
.sv — в избранное
.tag N/all — тегнуть
💉.tiktok — скачать тик ток
.timer 00:00:00 — таймер
💉.tp on/off — печатать
.t ru/en/uk -/on/off — переводчик
.ttl — время до удаления
.unzip/unrar(/-/f) — распаковать
.vrz 00:00:00 00:00:00 — вырезать
💉.vt — вирус-тотал
.watermark(f/v) — водяной знак
.wiki/wikifull — поиск википедия
.wipeaccount — очистить аккаунт
💉.youtube — скачать ютуб
.zmeyka — змейка
```"""
        await event.reply(text)