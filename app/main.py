import sys
from os import getenv
import logging
import random
from telethon import TelegramClient, events, Button
from sqlalchemy import select, and_

from classes import Hero, Monster, Base
from keyboards import inline_keyboards, reply_keyboards
from db import Main, Session
from forks.plots import (plots,
                         after_fight,
                         road_to_bow_with_arrows,
                         road_to_bow_without_arrows,
                         merchant,
                         confirm_trade,
                         not_confirm_trade,
                         forest,
                         monsters_plot,
                         guild_choice,
                         question_,
                         npc,
                         test_bow,
                         road_to_enchanter,
                         view_shop,
                         stroll_plot, 
                         find_boar
                         )

from forks.collision import start_collision

api_id = getenv("api_id")
api_hash = getenv('api_hash')
bot_token = getenv("bot_token")

print(api_hash)
print(api_id)
print(bot_token)

client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

heroes = {
    "Brew": Hero("Brew", 50, 5),
    "Aboba": Hero("Aboba", 80, 10),
    "Test": Hero("Test", 150, 75)
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
                del current_user_state[user_id]
            elif selected_hero == "Розпочати Гру!":
                pass
            else:
                del current_user_state[user_id]
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
                    await event.respond(f"Спроба втечі не вдалася. Твій герой має {hero.hp} здоров'я. Монстр все ще жив.\nЩо ти будеш робити?", buttons=inline_keyboards.first_hit)
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


selected_damage = 0
@client.on(events.CallbackQuery(pattern=b'choice_damage'))
async def fight(event):
    global selected_damage
    selected_damage = selected_damage + random.randint(0, 20)
    await event.respond(f"Твоя цифра = {selected_damage}", buttons=inline_keyboards.first_hit)
    global hero, user_id, monster_hp_value
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    hero = heroes.get(hero_name)
    monster_hp_value = monster_hp.get(user_id)

@client.on(events.CallbackQuery(pattern=b'first_hit'))
async def start_fight(event):
    global selected_damage
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    global hero
    hero = heroes.get(hero_name)
    monster_hp_value = monster_hp.get(user_id)

    if hero and monster_hp_value is not None and selected_damage is not None:
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
                user.hp = hero.hp
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
            buttons=inline_keyboards.first_hit
        )
    else:
        await event.respond("Проблеми з даними о героях або монстрах.")   



@client.on(events.CallbackQuery(pattern=b'use_heal'))
async def user_heal(event):
    sender = await event.get_sender()
    global hero
    first_name = sender.first_name
    try:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            
            if user is None:
                await event.respond("Користувача не знайдено.")
                return
            
            if user.heal <= 0:
                await event.respond("В тебе недостатньо хілок.")
                return
            user.heal -= 1
            user.hp += 15
            hero.hp += 15
            await event.edit(f"Ти використав 1 хілку, тепер в тебе їх {user.heal} шт.\nТа {hero.hp} хп")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")



traveler_path = "app/assets/traveler.jpg"
@client.on(events.CallbackQuery(pattern=b'go_1'))
async def go_1(event):
    global traveler_path
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
    first_name = sender.first_name

    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        if user.have_fight == 1:
            await event.respond(road_to_bow_with_arrows, buttons=inline_keyboards.next_3)
        else:
            await event.respond(road_to_bow_without_arrows, buttons=inline_keyboards.next_3)

    
@client.on(events.CallbackQuery(pattern=b'go_to_bow'))
async def go_to_bow(event):
    await event.respond("Цей поход буде нелегкий, тому пропоную випити тобі хілку", buttons=inline_keyboards.only_heal)
    await event.respond("Або можеш йти по хардкору та зберігти хілку", buttons=inline_keyboards.go_4)


@client.on(events.CallbackQuery(pattern= b'go_4'))
async def go_4(event):
    await event.respond(merchant, buttons=inline_keyboards.go_to_merchant)


@client.on(events.CallbackQuery(pattern=b'dialog_with_merchant'))
async def merchant_choice(event):
    await event.respond('Що ти обираєш зробити', buttons=inline_keyboards.merchant_choice)


@client.on(events.CallbackQuery(pattern=b'do_trade'))
async def do_trade(event):
    first_name = event.sender.first_name
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        if user.heal <= 0:
            await event.respond("Ти не можеш отримати гроші бо в тебе недостаньо хілок")
        else:
            user.coins += 20
            user.heal -= 1
            await event.respond(confirm_trade, buttons=inline_keyboards.go_6)
                 

@client.on(events.CallbackQuery(pattern=b'go_5'))
async def left_trade(event):        
    await event.respond(not_confirm_trade, buttons=inline_keyboards.go_6)


@client.on(events.CallbackQuery(pattern=b'go_6'))
async def go_6(event):
    await event.respond(forest, buttons=inline_keyboards.go_7)


@client.on(events.CallbackQuery(pattern=b'go_7'))
async def go_7(event):
    await event.respond(monsters_plot, buttons=inline_keyboards.start_gight_2)


@client.on(events.CallbackQuery(pattern=b'kick_2'))
async def hitting_2(event):
    await event.respond("Давай оберемо урон який тобі будуть зазначати монстри, на основі рандомного числа. чим більше число тим більше урон у монстрів", buttons=inline_keyboards.send_dice)


@client.on(events.CallbackQuery(pattern=b'dice'))
async def choice_monster_damage(event):
    global monster_damage_choice
    monster_damage_choice = random.randint(0, 10)
    await event.respond(f"Випало число = {monster_damage_choice}", buttons=inline_keyboards.next_8)


monster_hp_dict = {}

@client.on(events.CallbackQuery(pattern=b'next_8'))
async def next_8(event):
    monsters_ = [Monster("Gimno", 55, 5), Monster("Ben", 65, 7)]
    monster_hp = sum(monster.hp for monster in monsters_)
    
    path1 = "app/assets/monster1.gif"
    path2 = "app/assets/monster2.gif"

    await client.send_file(event.chat_id, path1)
    await client.send_file(event.chat_id, path2, caption=f"На тебе вийшло 2 монстри, їх хп в сумі = {monster_hp}")
    

    user_id = event.sender_id
    monster_hp_dict[user_id] = monster_hp
    
    await event.respond("Приготуйся до атаки!", buttons=inline_keyboards.final_attack_2)


def calculate_damage(hero: object, selected_damage: int):
    if 17 <= selected_damage <= 22:
        return hero.damage + random.randint(8, 10)
    elif 12 <= selected_damage <= 16:
        return hero.damage + random.randint(4, 7)
    elif 7 <= selected_damage <= 11:
        return hero.damage + random.randint(3, 5)
    elif 3 <= selected_damage <= 6:
        return hero.damage + 3
    elif 1 <= selected_damage <= 2:
        return hero.damage + 1
    elif selected_damage == 0:
        return hero.damage - 3
    else:
        return hero.damage


def calculate_monster_damage(monsters_, monster_damage_choice: int):
    start_total = sum(monster.damage for monster in monsters_)
    
    if monster_damage_choice <= 3:
        return start_total
    elif 4 <= monster_damage_choice <= 7:
        return start_total + random.randint(1, 2)
    elif 8 <= monster_damage_choice <= 10:
        return start_total + random.randint(2, 4)
    else:
        return monster_damage_choice


@client.on(events.CallbackQuery(pattern=b'do_attack'))
async def do_attack(event):
    sender = await event.get_sender()
    first_name = sender.first_name
    
    monsters_ = [Monster("Gimno", 55, 5), Monster("Ben", 65, 7)]
    global monster_damage_choice

    monster_damage = calculate_monster_damage(monsters_, monster_damage_choice)
    
    user_id = event.sender_id
    hero_name = user_heroes.get(user_id)
    hero = heroes.get(hero_name)
    selected_damage = random.randint(0, 20)

    if hero:
        damage_dealt = calculate_damage(hero, selected_damage)

        monster_hp_dict[user_id] -= damage_dealt

        if monster_hp_dict[user_id] <= 0:
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                user.heal += 2
                user.hp = hero.hp
                user.arrows += 5
                user.coins += 15
                await event.edit(
                    f"Монстр пав! Твій герой має {hero.hp} здоров'я.\nТобі випало:\n-Хілки: 2\nСтріли: 5\nМонети: 15\nТи можеш використати хілку щоб збільшити своє хп на 15\nКількість хілок: {user.heal}",
                    buttons=inline_keyboards.enter_1
                )
                await event.respond("Йти далі", buttons = inline_keyboards.without_heal)
                return

        hero.hp -= monster_damage
        if hero.hp <= 0:
            await event.respond(
                f"Твій герой був повержен монстром. Конец гри.",
                buttons=inline_keyboards.start_game
            )
            return

        await event.edit(
            f"Ти завдав {damage_dealt} урону. У монстрів залишилось {monster_hp_dict[user_id]} здоров'я.\n"
            f"Монстр нанес тобі урон - {monster_damage}\nУ тебе залишилось {hero.hp} здоров'я. Монстр все ще жив.\nПродовжуй битву!",
            buttons=inline_keyboards.final_attack_2
        )
    else:
        await event.respond("Проблеми з даними о героях або монстрах.")



@client.on(events.CallbackQuery(pattern=b'road_to_bow'))
async def road_to_bow(event):
    global traveler_path
    await client.send_file(event.chat_id, traveler_path, caption="Привіт, думаю ти мене памʼятаєш.\nЯ знову з вопросами.\nЯкий результат виконання виразу list(map(lambda x: x * 2, [1, 2, 3]))?", buttons=inline_keyboards.second_question)


@client.on(events.CallbackQuery(pattern=b'q2_.*'))
async def check_answer_2(event):
    correct_answer = b'q2_true'
    global first_name
    sender = await event.get_sender()
    user_id = event.sender_id
    first_name = sender.first_name
    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.arrows += 5
            user.heal += 1
        await event.respond("Молодець!\nПравильна відповідь, тримай 10➶➶\nТа 1 хілку🧪", buttons=inline_keyboards.enter_2)
    else:
        await event.respond("Тобі треба підтягнути знання у програмуванні, але нічого, ти переміг монстра та можеш йти далі", buttons=inline_keyboards.enter_2)


@client.on(events.CallbackQuery(pattern=b'enter_2'))
async def enter_2(event):
    guild_path = "app/assets/guild.png"
    await client.send_file(event.chat_id, guild_path, caption=guild_choice, buttons=inline_keyboards.guild_choice)
    

@client.on(events.CallbackQuery(pattern=b'guild_.*'))
async def save_user_guild(event):
    global first_name
    
    try:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            if user is None:
                await event.respond("Користувача не знайдено.")
                return
            
            if user.guild == "NOTHING":
                match event.data:
                    case b'guild_mages':
                        user.guild = "Mages"
                    case b'guild_fighters':
                        user.guild = "Fighters"
                    case b'guild_trackers':
                        user.guild = "Trackers"
                    case _:
                        await event.respond("Помилка при виборі гільдії")
                        return
            else:
                await event.respond("Неможна переобрати гільдію")
                return
            
            session.add(user)
            await event.respond(f"Обрана гільдія: {user.guild}", buttons=inline_keyboards.action_guild_1)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")


@client.on(events.CallbackQuery(pattern=b'action_guild_1'))
async def guild_action_1(event):
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        guild = user.guild
    guild_member_path = "app/assets/guild_member.gif"
    await client.send_file(event.chat_id, guild_member_path, caption=question_, buttons=inline_keyboards.third_question)

@client.on(events.CallbackQuery(pattern=b'q3_.*'))
async def check_answer_3(event):
    correct_answer = b'q3_true'
    global first_name

    try:
        if event.data == correct_answer:
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                if user is None:
                    await event.respond("Користувача не знайдено")
                    return

                match user.guild:
                    case "Mages":
                        user.slot = "lucky"
                        await event.respond("Правильно, тримай собі + к удачі, це не буде зайвим", buttons=inline_keyboards.enter_3)
                    case "Fighters":
                        user.arrows += 15
                        await event.respond("Вітаємо, ти не даремно обрав нашу гільдію - тримай 15 стріл➶➶", buttons=inline_keyboards.enter_3)
                    case "Trackers":
                        user.slot += "fireball"
                        await event.respond("Ключ до успіху з нашою гільдією, тобі за правильну відповідь дається фаєр-бол💥", buttons=inline_keyboards.enter_3)
                    case _:
                        await event.respond("Сталася помилка при обробці надавання призу")

        else:
            await event.respond("У нашій гільдії необхідно знати відповіді на такі питання, але ти тільки новачок, тому все ще попереду, а за вступ у гільдію тримай 10 монет 🪙", buttons=inline_keyboards.enter_3)
            with Session.begin() as session:
                user = session.scalar(select(Main).where(Main.username == first_name))
                if user is None:
                    await event.respond("Користувача не знайдено")
                    return
                user.coins += 10
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")




@client.on(events.CallbackQuery(pattern=b'enter_3'))
async def enter_3(event):
    await event.respond("Псс, ти вже трішки розвинений в нашому світі, тому тобі відкривається функція перегляду інвентаря твого персонажу\n/dossier\nПотім можеш йти далі", buttons=inline_keyboards.enter_4)


@client.on(events.NewMessage(pattern="/dossier"))
async def wiew_dossier(event):
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        await event.respond(f"""Статистика юзера: 👤 <b>{user.username}</b>\n
Герой: {user.hero} 🦸
Хп: {user.hp} ♥️
Хілки: {user.heal} 🧪
Стріли: {user.arrows} ➶➶
Монети: {user.coins} 🪙
Гільдія: {user.guild} 🔱
Слот: {user.slot} 🧩
                            """, parse_mode='html')
        

@client.on(events.CallbackQuery(pattern=b'enter_4'))
async def enter_4(event):
    location1_path = "app/assets/location1.png"
    await client.send_file(event.chat_id, location1_path, caption=npc, buttons=inline_keyboards.quest_for_npc)

@client.on(events.CallbackQuery(pattern=b'quest_for_npc'))
async def quest_for_npc(event):
    await event.respond("Ми ще не настільки знайомі з тобою, пізніше ти може дізнєшься чого я знаю про тебе стільки всього, а зараз - твоя задача це забрати лук", buttons=inline_keyboards.enter_5)


@client.on(events.CallbackQuery(pattern=b'enter_5'))
async def enter_5(event):
    forest_path = "app/assets/location2.png"
    await client.send_file(event.chat_id, forest_path, caption="Ти йдеш по лісу і бачиш багато оленів\nНу шо, кидаємо кості?", buttons=inline_keyboards.third_fight)



hp_dict = dict()
number_generated = {}
user_options = {}

@client.on(events.CallbackQuery(pattern=b'fight_3'))
async def fight_3(event):
    user_id = event.sender_id
    
    if user_id in number_generated:
        await event.respond("Ви вже отримали число!")
        return

    number = random.randint(0, 20)
    number_generated[user_id] = number
    user_options[user_id] = None
    await event.respond(f"Тобі випало число {number}", buttons=inline_keyboards.do_hit)


@client.on(events.CallbackQuery(pattern=b'do_hit'))
async def do_hit(event):
    monsters = [
                    Monster("Reindeer1", 25, 5),
                    Monster("Reindeer2", 25, 5),
                    Monster("Reindeer3", 25, 5)
                ]
    user_id = event.sender_id
    number = number_generated.get(user_id)
    if number is None:
        await event.respond("Спочатку потрібно отримати число!")
        return

    monster_hp = 100
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))


        if user.slot == "fireball":
            if user_options[user_id] is None:
                remaining_hp = hp_dict.get(user_id, monster_hp) - 25
                hp_dict[user_id] = remaining_hp
                user.slot = ""
                user_options[user_id] = "fireball"
                await event.respond("В тебе є файр-бол, він летить у оленів\nОленів становиться на одного меньше\nВже 3 оленя!\nУ оленів 85хп")
                
            else:
                monsters_ = monsters
        
        elif user.slot == "lucky":
            if user_options[user_id] is None:
                number += 2
                user.slot = ""
                user_options[user_id] = "lucky"
                await event.respond(f"В тебе в інвентарі є удача, к твому рандому числу + 2\nВипадкове число тепер дорівнює = {number}")
                monsters_ = [
                    Monster("Reindeer1", 25, 5),
                    Monster("Reindeer2", 25, 5),
                    Monster("Reindeer3", 25, 5),
                    Monster("Reindeer4", 25, 5)
                ]

        
        elif user.arrows >= 15:
            if user_options[user_id] is None:
                remaining_hp = hp_dict.get(user_id, monster_hp) - 25
                hp_dict[user_id] = remaining_hp
                user.arrows -= 15
                user_options[user_id] = "arrows" 
                await event.respond("Ти як справжній міщанин затикав копʼєм оленя і тепер оленів на одного меньше\nХп оленів: 85")
                monsters_ = monsters
            else:
                monsters_ = monsters

        hp_dict[user_id] = hp_dict.get(user_id, monster_hp)

        monster_damage_choice = number
        monster_damage = calculate_monster_damage(monsters_, monster_damage_choice)

        hero_name = user_heroes.get(user_id)
        hero = heroes.get(hero_name)

        if hero:
            damage_dealt = calculate_damage(hero, selected_damage=number)

            hp_dict[user_id] -= damage_dealt
            if hp_dict[user_id] <= 0:
                user.hp += 25
                user.coins += 10
                await event.edit(f'Ти люто нагнув оленів во всіх формах цього слова\nЗ них випало 10 монет і тобі +25 хп\nТепер в тебе {user.hp}', buttons=inline_keyboards.walk)
                number_generated.pop(user_id, None)
                return
            
            hero.hp -= monster_damage
            user.hp -= monster_damage
            if user.hp <= 0:
                await event.edit("Ти з позором впав перед оленямі ахахахаха")
                return
            
            await event.edit(f"- Ти задав {damage_dealt} урону\nУ оленів {hp_dict.get(user_id)}\n- Олень задав тобі {monster_damage} урону\nУ тебе {user.hp}", buttons=inline_keyboards.do_hit)


@client.on(events.CallbackQuery(pattern=b'back'))
async def go_back(event):
    back_choice_path = "app/assets/back_choice.png"
    await client.send_file(event.chat_id, back_choice_path, caption="Бачиш, він теж обирає зад, тільки не в плані подорожей\nВже немає дороги назад)", buttons=inline_keyboards.however_walk)


@client.on(events.CallbackQuery(pattern=b'walk_to_bow'))
async def walk_to_bow(event):
    сlosed_gates_path = "app/assets/closed_gates.png"
    await client.send_file(event.chat_id, сlosed_gates_path, caption="Лук зараз закритий,треба відповісти на 3 запитання", buttons=inline_keyboards.open_test)


@client.on(events.CallbackQuery(pattern=b'open_test'))
async def open_test(event):
    await event.respond("Перше питання!\n Який результат виконання виразу any([i > 2 for i in [1, 2, 3]])?", buttons=inline_keyboards.question_four)
    
@client.on(events.CallbackQuery(pattern=b'q4_.*'))
async def check_answer_4(event):
    correct_answer = b'q4_true'

    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.сorrect_answers += 1
        await event.respond("В тебе тепер 1 правильна відповідь", buttons=inline_keyboards.next_question1)
    else:
        await event.respond("Спробуй ще раз")


@client.on(events.CallbackQuery(pattern=b'next_question1'))
async def send_question_1(event):
    await event.respond("""Що поверне цей код\na = {i: i+2 for i in range(4)}.values()\n
print(a)
""", buttons=inline_keyboards.question_five)
    

@client.on(events.CallbackQuery(pattern=b'q5_.*'))
async def check_answer_5(event):
    correct_answer = b'q5_true'

    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.сorrect_answers += 1
        await event.respond("Правильно!", buttons=inline_keyboards.next_question2)
    else:
        await event.respond("Спробуй ще раз")


@client.on(events.CallbackQuery(pattern=b'next_question2'))
async def send_auestion_2(event):
    await event.respond("Фінальне запитання\nЩо поверне программа\n''.join([chr(i) for i in range(97, 102)])",buttons=inline_keyboards.question_six)


@client.on(events.CallbackQuery(pattern=b'q6_.*'))
async def check_answer_6(event):
    correct_answer = b'q6_true'

    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.сorrect_answers += 1
        await event.respond("Правильно!", buttons=inline_keyboards.run)
    else:
        await event.respond("Спробуй ще раз")


@client.on(events.CallbackQuery(pattern=b'run'))
async def run(event):
    open_gates_path = "app/assets/open_gates.gif"
    await client.send_file(event.chat_id, open_gates_path, caption="Двері відчиняються...))", buttons=inline_keyboards.run1)


@client.on(events.CallbackQuery(pattern=b'open_door'))
async def place_bow(event):
    bow_location_path = "app/assets/bow.jpg"
    await client.send_file(event.chat_id, bow_location_path, caption="І ОСЬ ВІН ПЕРЕД ТОБОЮ БЕРИ ЙОГО ", buttons=inline_keyboards.get_bow)


@client.on(events.CallbackQuery(pattern=b'get_bow'))
async def get_bow(event):
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        user.weapon = "bow"
    await event.respond("Поздравляємо від лиця автора і всіх нпс з твоєю новою зброєю, тепер будеш виносити опрнентів з дистанції", buttons=inline_keyboards.go_home)


@client.on(events.CallbackQuery(pattern=b'go_home'))
async def road_to_home(event):
    bat_path = "app/assets/bat.gif"
    await client.send_file(event.chat_id, bat_path, caption=test_bow, buttons=inline_keyboards.kill_bat)


@client.on(events.CallbackQuery(pattern=b'kill_bat'))
async def kill_bat(event):
    number = random.randint(1, 2)
    if number == 1 or number == 2:
        await event.respond("Ти непогано впрорався з луком,тобі випав огонь, по приходу додому - розкажу як ти можеш його використати, гарний початок", buttons=inline_keyboards.comeback_to_guild)
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.slot = "fire"
    else:
        await event.respond("Ти промазав, спугнув мишу та вона улетіла, нічого, це перша спроба", buttons=inline_keyboards.comeback_to_guild)


@client.on(events.CallbackQuery(pattern=b'comeback_to_guild'))
async def comeback_to_guild(event):
    guild_place_path = "app/assets/location1.png"
    await client.send_file(event.chat_id, guild_place_path, caption=road_to_enchanter, buttons=inline_keyboards.thx)
        

@client.on(events.CallbackQuery(pattern=b'thx'))
async def thx(event):
    guard_location_path = "app/assets/guardian.gif"
    await client.send_file(event.chat_id, guard_location_path, caption="Охоронець: Слухай, я тебе тут не бачив ще", buttons=inline_keyboards.for_guard)


@client.on(events.CallbackQuery(pattern=b'for_guard'))
async def for_guard(event):
    await event.respond("Відповідь на моє запитання і йди до чарівника\nЯкий результат виконання виразу {i: i**3 for i in range(3)}[2]?", buttons=inline_keyboards.aisle_question)


@client.on(events.CallbackQuery(pattern=b'q7_.*'))
async def check_answer_6(event):
    correct_answer = b'q7_true'

    if event.data == correct_answer:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            user.сorrect_answers += 1
        await event.respond("Проходь!)", buttons=inline_keyboards.meet_enchanter)
    else:
        await event.respond("Нажаль не можу тебе пропустити")


@client.on(events.CallbackQuery(pattern=b'meet_enchanter'))
async def meet_enchanter(event):
    await event.respond("Ох, привіт!Я чув шо в тебе є лук\nТи ж прийшов його зачарувати в мене, для цього потрібно або дати мені огонь який ти можеш здобути з вбивства кажана, або купити в мене за 10 монет\nЯкий варіант більше подобається?", buttons=inline_keyboards.enchanter_choice)


@client.on(events.CallbackQuery(pattern=b'have_fire'))
async def have_fire(event):
    try:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            if user is None:
                await event.respond("Користувача не знайдено")
                return

            if user.slot != "fire":
                await event.respond("В тебе немає огня, тому тобі треба його купити", buttons=inline_keyboards.buy)
            else:
                user.slot = ""
                user.weapon = "fire-bow"
                await event.respond("Тримай свій оновлений лук - вогнений лук!", buttons=inline_keyboards.return_to_base)
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")



@client.on(events.CallbackQuery(pattern=b'buy'))
async def buy(event):
    try:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            if user is None:
                await event.respond("Користувача не знайдено")
                return

            if user.coins < 10:
                await event.respond("Ви маєте недостатньо монет")
            else:
                user.coins -= 10
                await event.respond("Окей, гарна угода!", buttons=inline_keyboards.return_to_base)
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")



@client.on(events.CallbackQuery(pattern=b'return_to_base'))
async def return_to_base(event):
    await event.respond("Як же тут гарно вночі!", buttons=inline_keyboards.visit_shop)


@client.on(events.CallbackQuery(pattern=b'visit_shop'))
async def visit_shop(event):
    await event.respond(view_shop)



@client.on(events.NewMessage(pattern='/shop'))
async def shop(event):
    shop_path = "app/assets/shop.png"
    await client.send_file(event.chat_id, shop_path, caption="Зaходь до нас!\nТрапеза:", buttons=inline_keyboards.shop)
    await event.respond("Чи можеш йти далі", buttons=inline_keyboards.stroll)


PRODUCTS = {
    b'shop_zapikanka': (12, 10),
    b'shop_kasha': (5, 4),
    b'shop_hleb': (8, 9),
    b'shop_soup': (15, 15),
    b'shop_svinina': (22, 17)
}


@client.on(events.CallbackQuery(pattern=b'shop_.*'))
async def buy_product(event):
    product = PRODUCTS.get(event.data)
    if product is None:
        await event.respond("Сталася помилка")
        return
    cost, hp_increase = product
    
    try:
        with Session.begin() as session:
            user = session.scalar(select(Main).where(Main.username == first_name))
            if user is None:
                await event.respond("Користувача не знайдено")
                return
            if user.coins >= cost:
                user.hp += hp_increase
                user.coins -= cost
                num = random.randint(1, 2)
                response_message = (
                    "Приємного апетиту! Пам'ятайте, що якщо їсти швидко, калорії не встигають за вами!"
                    if num == 1
                    else "Смачного! Нехай ваш шлунок не знає відпочинку!"
                )
                await event.respond(response_message)
            else:
                await event.respond("Недостатньо монет")
    except Exception as e:
        print(f"An error occurred: {e}")
        await event.respond("Сталася помилка при обробці вашого запиту. Спробуйте ще раз пізніше.")



@client.on(events.CallbackQuery(pattern=b'stroll'))
async def stroll(event):
    await event.respond(stroll_plot, buttons=inline_keyboards.help_npc)


@client.on(events.CallbackQuery(pattern=b'help'))
async def help_npc(event):
    await event.respond(find_boar, buttons=inline_keyboards.go_hunting)


@client.on(events.CallbackQuery(pattern=b'go_hunting'))
async def go_hunting(event):
    await event.respond("Ви обережно ходите по лісу у пошуках кабана\nІ тут Сон говорить що бачить у кустах кабана,в тебе ж є лук,бери його і стріляй в кабана!", buttons=inline_keyboards.hit_the_boar)

def random_():
    """arg1 = 1 ; arg2 = 2 ; return random integer"""
    number = random.randint(1, 2)
    return number


@client.on(events.CallbackQuery(pattern=b'hit_the_boar'))
async def hit_the_boar(event):
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        user.arrows -= 1
    global died_boars
    died_boars = 0
    number = random_()
    if number == 1:
        await event.respond("Попадання! В нас вже 1/4 сердець є!", buttons=inline_keyboards.walk_in_forest)
        died_boars += 1
    else:
        await event.respond("Прмах( Нічого, ще ціла ніч попереду", buttons=inline_keyboards.walk_in_forest)


@client.on(events.CallbackQuery(pattern=b'walk_in_forest')) 
async def walk_in_forest(event):
    await event.respond("Ти ходив по лісу та через непроглядну темрявуви не побачили як підійшли до кабана зовсім близько, местра 3 була відстань, стріляй в нього поки ві не накнувся на тебе",buttons=inline_keyboards.second_hit)


def hero_damage():
    """return random int from 0 to 20"""
    number = random.randint(0, 20)
    return number

@client.on(events.CallbackQuery(pattern=b'second_hit'))
async def second_hit(event):

    global died_boars
    damage = hero_damage()
    boar_damage = random.randint(5, 15)

    if 'boar_hp' not in globals():
        global boar_hp
        boar_hp = 110

    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        user.hp -= boar_damage
        if user.hp > 0 and boar_hp > 0:
            boar_hp -= damage
            await event.edit(f"Ти надав монстру {damage} урону - тепер в нього {boar_hp}\nВін задав тобі {boar_damage} урону, в тебе {user.hp}хп", buttons=inline_keyboards.second_hit)
    
        elif user.hp <= 0:
            await event.respond("Тебе вбив кабан")
        elif boar_hp <= 0:
            await event.respond("Ти вбив кабана", buttons=inline_keyboards.give_coins)

@client.on(events.CallbackQuery(pattern=b'give_coins'))
async def give_coins(event):
    await event.respond("Тримай 35 монет за те що допоміг мені")
    with Session.begin() as session:
        user = session.scalar(select(Main).where(Main.username == first_name))
        user.coins += 35
        await event.respond("Розробник встиг все що зміг зробити за тиждень, та у випадку перемоги обіцяє підтрмати свій продукт да зробити форум для публыкації цілавиш моментов, ідей і тд у цій грі, всім бажаю гарного дня та приємного геймплею!!!!!")

        

    
async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    client.loop.run_until_complete(main())