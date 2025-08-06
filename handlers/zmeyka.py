import asyncio
import random
from telethon import events

game_state = {}

directions = {
    ".a": (-1, 0),  #влево
    ".w": (0, -1),  #вверх
    ".s": (1, 0),   #вправо
    ".z": (0, 1),   #вниз
}

def render_game(state):
    field = [["⿴" for _ in range(10)] for _ in range(10)]
    for x, y in state["snake"]:
        field[y][x] = "🟢"
    head_x, head_y = state["snake"][-1]
    field[head_y][head_x] = "🟩"
    fx, fy = state["food"]
    field[fy][fx] = "🍎"
    return "\n".join("".join(row) for row in field)

def spawn_food(snake):
    while True:
        pos = (random.randint(0, 9), random.randint(0, 9))
        if pos not in snake:
            return pos

async def game_loop(chat_id):
    while chat_id in game_state:
        await asyncio.sleep(1.2)
        state = game_state.get(chat_id)
        if not state:
            break

        dx, dy = state["dir"]
        snake = state["snake"]
        head_x, head_y = snake[-1]
        new_head = ((head_x + dx) % 10, (head_y + dy) % 10)

        if new_head in snake:
            await state["msg"].edit("**змейка врезалась в себя!**")
            game_state.pop(chat_id, None)
            break

        snake.append(new_head)
        if new_head == state["food"]:
            state["score"] += 1
            state["food"] = spawn_food(snake)
        else:
            snake.pop(0)

        await state["msg"].edit(f"**Змейка • Счёт: {state['score']}**\n\n{render_game(state)}")

def register(client):
    @client.on(events.NewMessage(outgoing=True, pattern=r"\.zmeyka"))
    async def start_game(event):
        chat_id = event.chat_id
        if chat_id in game_state:
            await event.respond("**змейка уже запущена.**")
            return

        snake = [(4, 5), (5, 5)]
        food = spawn_food(snake)
        msg = await event.respond(
            f"**змейка запущена!**\nУправление: .w .a .s .z .zstop - пауза\nСчёт: 0\n\n{render_game({'snake': snake, 'food': food})}"
        )

        game_state[chat_id] = {
            "snake": snake,
            "food": food,
            "msg": msg,
            "score": 0,
            "dir": (1, 0)
        }

        asyncio.create_task(game_loop(chat_id))

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.(w|a|s|z)"))
    async def change_direction(event):
        await event.delete()
        chat_id = event.chat_id
        if chat_id not in game_state:
            return

        text = event.raw_text
        if text not in directions:
            return

        dx, dy = directions[text]
        cur_dx, cur_dy = game_state[chat_id]["dir"]

        if (dx, dy) == (-cur_dx, -cur_dy):
            return  

        game_state[chat_id]["dir"] = (dx, dy)

    @client.on(events.NewMessage(outgoing=True, pattern=r"\.zstop"))
    async def stop_game(event):
        chat_id = event.chat_id
        if chat_id in game_state:
            game_state.pop(chat_id)
            await event.respond("**змейка остановлена.**")
        else:
            await event.respond("**змейка не запущена.**")