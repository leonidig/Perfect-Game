from telethon import Button as button


start_game = [
    button.inline('Запуск гри', b'start')
]

choice_plot = [
    button.inline("🎲", b'choice_plot')
]

go_to_fight = [
    button.inline("Далі", b'next1')
]


choice_in_fight = [
    [button.inline("Битися", b'FIGHT')],
    [button.inline("Втікти", b'LAVE')]
]


use_heal = [
    [button.inline("Використати(+15 хп)", b'use_heal')]
]

choice_damage = [
    button.inline("🎲", b'choice_damage')
]
start_gight = [
    button.inline("Почати Битву", b'start_gight')
]

kick = [
    button.inline("Вдприти!", b"kick")
]