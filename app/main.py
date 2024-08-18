import sys
from os import getenv
import logging
from telethon import TelegramClient, events
from sqlalchemy import select

from classes import Hero, Base
from keyboards import inline_keyboards, reply_keyboards
from db import Main, Session



api_id = getenv("api_id")
api_hash = getenv('api_hash')
bot_token = getenv("bot_token")


client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

global heroes

heroes = {
    "Brew" : Hero("Brew", 50, 5),
    "Aboba": Hero("Aboba", 80, 10)
}

current_user_state = {}


@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    sender = await event.get_sender()
    user_id = event.sender_id
    global first_name
    first_name = sender.first_name
    await event.respond(f"Привіт! {first_name}.Ти потрапив у світ битв з монстрами та захоплюючими подорожами по казковому світу.", buttons = reply_keyboards.start_game)
    

@client.on(events.NewMessage(pattern="Розпочати Гру!"))
async def test(event):
    await event.respond("Дивись які є персонажі, щоб обрати одного з них - напиши його імʼя: ")

    for hero in heroes.values():
        await event.respond(f'''
- Імʼя : {hero.name}
- Здоровїʼя: {hero.hp}
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
                    user = Main(username=first_name, hero=selected_hero)
                    session.add(user)
                await event.respond(f"Твій вибір пав на: {selected_hero}\nПодивимось чи впорається він з усіма складностями")
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