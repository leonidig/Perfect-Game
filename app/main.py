import sys
from os import getenv
import logging
import random
from telethon import TelegramClient, events, Button
from sqlalchemy import select

from classes import Hero, Monster, Base
from keyboards import inline_keyboards, reply_keyboards
from db import Main, Session
from forks.start_plot import plots
from forks.collision import start_collision

api_id = getenv("api_id")
api_hash = getenv('api_hash')
bot_token = getenv("bot_token")

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

heroes = {
    "Brew": Hero("Brew", 50, 5),
    "Aboba": Hero("Aboba", 80, 10)
}

monsters = [Monster("Grew", 40, 5), Monster("Gabgala", 60, 10)]

current_user_state = {}
user_plots = {}
user_heroes = {}
monster_hp = {}


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    await event.respond(f"Привіт, {first_name}! Ти потрапив у світ битв з монстрами та захоплюючими подорожами по казковому світу.", buttons=reply_keyboards.start_game)


@client.on(events.CallbackQuery(pattern=b'start'))
async def start_game(event):
    await event.respond("Кинути кубік ->", buttons=inline_keyboards.choice_plot)


@client.on(events.CallbackQuery(pattern=b'choice_plot'))
async def choice_plot(event):
    user_id = event.sender_id

    if user_id in user_plots:
        await event.respond(f"Ти вже обрав сюжет\nВін не може бути змінений.")
    else:
        selected_plot_key = random.choice(list(plots.keys()))
        user_plots[user_id] = selected_plot_key
        cave_path = "app/assets/cave.jpg"
        forest_path = "app/assets/forest.jpg"
        future_path = 'app/assets/future.jpg'
        selected_plot_path = (cave_path if selected_plot_key == "plot3" else forest_path if selected_plot_key == "plot1" else future_path)
        await client.send_file(event.chat_id, selected_plot_path, caption=f"Тобі випав сюжет ->\n{plots[selected_plot_key]}", buttons=inline_keyboards.go_to_fight)



def select_monster():
    global monster
    monster = random.choice(monsters)
    return monster


@client.on(events.CallbackQuery(pattern=b'next1'))
async def go_to_fight(event):
    user_id = event.sender_id
    monster = select_monster()
    monster_hp[user_id] = monster.hp
    user_hero = heroes.get(user_heroes.get(user_id))
    
    if user_hero:
        await event.respond(start_collision + "\nІ тут на тебе виходить...\n" + f"Імʼя: {monster.name}\nЗдоровʼя: {monster.hp}\nУрон: {monster.damage}", buttons=inline_keyboards.choice_in_fight)
    else:
        await event.respond("Вибери героя спочатку.")


@client.on(events.CallbackQuery(pattern=b'FIGHT'))
async def fight(event):
    global hero
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    hero = heroes.get(hero_name)
    monster_hp_value = monster_hp.get(user_id)
    
    if hero and monster_hp_value is not None:
        damage_dealt = hero.damage
        monster_hp[user_id] -= damage_dealt
        
        if monster_hp[user_id] <= 0:
            sender = await event.get_sender()
            first_name = sender.first_name
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                user.heal += 1
                await event.respond(
                    f"Монстр пав! Твій герой має {hero.hp} здоров'я.\nТи можеш викоритати хілку щоб збільшити своє хп на 15(у тебе {user.heal} хілок)",
                    buttons=inline_keyboards.use_heal
                )
                return

        damage = monster.damage
        hero.hp -= damage
        if hero.hp <= 0:
            await event.respond(
                f"Твій герой був повержен монстром. Конец гри.",
                buttons=inline_keyboards.start_game
            )
            return

        await event.edit(
            f"Ти завдав {monster.name} {damage_dealt} урону.У {monster.name} залишилось {monster_hp[user_id]} здоров'я."
            f"Монстр нанес тобі урон - {damage}\nу тебе залишилось {hero.hp} здоров'я. Монстр все ще жив.\nПродовжуй битву!",
            buttons=inline_keyboards.choice_in_fight
        )
    else:
        await event.respond("Проблеми з даними о героях або монстрах.")


@client.on(events.CallbackQuery(pattern=b'use_heal'))
async def user_heal(event):
    sender = await event.get_sender()
    first_name = sender.first_name
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        user.heal -= 1
        hero.hp += 15
        await event.respond(f"Ти використав 1 хілку, тепер в тебе їх {user.heal}\nТа {hero.hp}")


@client.on(events.CallbackQuery(pattern=b'LAVE'))
async def escape(event):
    user_id = event.sender_id
    if random.randint(0, 1) == 0:
        await event.respond("Тобі вдалося втекти!")
    else:
        hero_name = user_heroes.get(user_id)
        hero = heroes.get(hero_name)
        if hero:
            hero.hp -= 10
            if hero.hp <= 0:
                await event.respond(f"Ти спробував втекти, але монстр наздогнав тебе і переміг. Конец гри.")
            else:
                await event.respond(f"Спроба втечі не вдалася. Твій герой має {hero.hp} здоров'я. Монстр все ще жив.\nЩо ти будеш робити?", buttons=inline_keyboards.choice_in_fight)
        else:
            await event.respond("Вибери героя спочатку.")


@client.on(events.NewMessage(pattern="Розпочати Гру!"))
async def choice_hero(event):
    await event.respond("Дивись які є персонажі, щоб обрати одного з них - напиши його імʼя: ")

    for hero in heroes.values():
        await event.respond(f'''
- Імʼя: {hero.name}
- Здоровʼя: {hero.hp}
- Урон: {hero.damage}
''')

    user_id = event.sender_id
    current_user_state[user_id] = 'waiting_for_choice'


@client.on(events.NewMessage())
async def handle_message(event):
    user_id = event.sender_id

    if user_id in current_user_state:
        state = current_user_state[user_id]

        if state == 'waiting_for_choice':
            selected_hero = event.text
            if selected_hero in heroes.keys():
                with Session.begin() as session:
                    user = Main(username=event.sender.first_name, hero=selected_hero)
                    session.add(user)
                user_heroes[user_id] = selected_hero
                await event.respond(f"Твій вибір пав на: {selected_hero}\nПодивимось, чи впорається він з усіма складностями.", buttons=inline_keyboards.start_game)
            elif selected_hero == "Розпочати Гру!":
                pass
            else:
                await event.respond("Герой не знайден (")


async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    client.loop.run_until_complete(main())
    