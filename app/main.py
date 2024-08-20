import sys
from os import getenv
import logging
import random
from telethon import TelegramClient, events, Button
from sqlalchemy import select

from classes import Hero, Monster, Base
from keyboards import inline_keyboards, reply_keyboards
from db import Main, Session
from forks.plots import plots, after_fight, road_to_bow_with_arrows, road_to_bow_without_arrows
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
go_or_heal = {}
user_heroes = {}
monster_hp = {}


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    await event.respond(f"Привіт, {first_name}! Ти потрапив у світ битв з монстрами та захоплюючими подорожами по казковому світу.", buttons=reply_keyboards.start_game)

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
            selected_hero = event.text.title()
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
        monster_path = "app/assets/gabgala.gif" if monster.name == "Gabgala" else "app/assets/grew.gif"
        await client.send_file(event.chat_id, monster_path, caption=f"{start_collision}\nІ тут на тебе виходить...\n" + f"Імʼя: {monster.name}\nЗдоровʼя: {monster.hp}\nУрон: {monster.damage}", buttons=inline_keyboards.choice_in_fight)
    else:
        await event.respond("Вибери героя спочатку.")

@client.on(events.CallbackQuery(pattern=b'LAVE'))
async def escape(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    if user_id in go_or_heal:
        await event.respond("Ну будь як мужик, ти захотів битися - бийся\nА я тільки посміюсь з твоєї жалюгідної спроби втекти")
    else:
        go_or_heal[user_id] = "leave"
        if random.randint(0, 1) == 0:
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                user.have_fight = False
            await event.respond("Тобі вдалося втекти!", buttons=inline_keyboards.next_2)
        else:
            hero_name = user_heroes.get(user_id)
            hero = heroes.get(hero_name)
            if hero:
                hero.hp -= 10
                if hero.hp <= 0:
                    await event.respond(f"Ти спробував втекти, але монстр наздогнав тебе і переміг. Конец гри.")
                else:
                    await event.respond(f"Спроба втечі не вдалася. Твій герой має {hero.hp} здоров'я. Монстр все ще жив.\nЩо ти будеш робити?", buttons=inline_keyboards.kick)
            else:
                await event.respond("Вибери героя спочатку.")


@client.on(events.CallbackQuery(pattern=b'FIGHT'))
async def choice_damage(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    if user_id in go_or_heal:
        await event.respond("Ти вже обрав подію, її ти не можеш зміти свій вибір")
    else:
        go_or_heal[user_id] = "fight"
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.have_fight = True
        await event.respond("Ти сам захотів цю бійку\nНатисни на кубик щоб випробовувати свою удачу", buttons=inline_keyboards.choice_damage)


@client.on(events.CallbackQuery(pattern=b'choice_damage'))
async def fight(event):
    global selected_damage
    selected_damage = random.randint(0, 20)
    await event.respond(f"Твоя цифра =  {selected_damage}", buttons=inline_keyboards.kick)
    global hero, user_id, monster_hp_value
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    hero = heroes.get(hero_name)
    monster_hp_value = monster_hp.get(user_id)

    
    
@client.on(events.CallbackQuery(pattern=b'kick'))
async def start_fight(event):
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    hero = heroes.get(hero_name)
    monster_hp_value = monster_hp.get(user_id)
    if hero and monster_hp_value is not None:
        damage_dealt = (
    hero.damage + random.randint(4, 7) if 17 <= selected_damage <= 20 else
    hero.damage + random.randint(2, 5) if 12 <= selected_damage <= 16 else
    hero.damage + random.randint(1, 3) if 7 <= selected_damage <= 11 else
    hero.damage + 1 if 3 <= selected_damage <= 6 else
    hero.damage if 1 <= selected_damage <= 2 else
    hero.damage - 5 if selected_damage == 0 else
    hero.damage
)


        monster_hp[user_id] -= damage_dealt
        
        if monster_hp[user_id] <= 0:
            sender = await event.get_sender()
            first_name = sender.first_name
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                user.heal += 1
                await event.edit(
                    f"Монстр пав! Твій герой має {hero.hp} здоров'я.\nТобі випала 1 хілка\nТи можеш використати хілку щоб збільшити своє хп на 15\nКількість хілок: {user.heal}",
                    buttons=inline_keyboards.go_or_heal
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
            buttons=inline_keyboards.kick
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
        await event.edit(f"Ти використав 1 хілку, тепер в тебе їх {user.heal} шт.\nТа {hero.hp} хп", buttons=inline_keyboards.go_1)

@client.on(events.CallbackQuery(pattern=b'go_1'))
async def go_1(event):
    traveler_path = "app/assets/traveler.jpg"
    await client.send_file(event.chat_id, traveler_path, caption=after_fight)
    await event.respond("Дай мені відповідь на запитання, і отримаєш стріли", buttons=inline_keyboards.arrows_choice)


@client.on(events.CallbackQuery)
async def first_task(event):
    if event.data == b"answer_choice":
        await event.respond("Який результат виконання виразу\n{1, 2, 3} & {2, 3, 4}", buttons=inline_keyboards.first_question)


@client.on(events.CallbackQuery(pattern=b'q1_.*'))
async def check_answer_1(event):
    correct_answer = b'q1_true'
    sender = await event.get_sender()
    first_name = sender.first_name
    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.arrows += 10
        await event.respond("Молодець!\nПравильна відповідь, тримай 10➶➶", buttons=inline_keyboards.next_2)
    else:
        await event.respond("Тобі треба підтягнути знання у програмуванні, але нічого, ти переміг монстра та можеш йти далі", buttons=inline_keyboards.next_2)



@client.on(events.CallbackQuery(pattern=b'next_2'))
async def go_to_church(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        if user.have_fight:
            await event.respond(road_to_bow_with_arrows)
        else:
            await event.respond(road_to_bow_without_arrows, buttons=inline_keyboards.next_3)

    
@client.on(events.CallbackQuery(pattern=b'go_to_bow'))
async def go_to_bow(event):
    await event.respond("Цей поход буде нелегкий, тому пропоную випити тобі хілку")



async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    client.loop.run_until_complete(main())
    