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


go_or_heal = [
    [button.inline("Використати(+15 хп)", b'use_heal')],
    [button.inline("Залишити та йти далі", b'go_1')]
]

only_go = [
    button.inline("Йти далі", b'go_1')
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

go_1 = [
    button.inline("Йти далі",  b'go_1')
]


arrows_choice = [
    [button.inline("Відповісти", b"answer_choice")],
    [button.inline("Йти далі та не отримати стріли", b'next_2')]
]


first_question = [
    [button.inline("{1, 2, 3, 4}",  b'q1_false_1')],
    [button.inline("{2, 3}",  b'q1_true')],
    [button.inline("{1, 3}",  b'q1_false_2')],
    [button.inline("{1, 4}",  b'q1_false_3')]
]


next_2 = [
    button.inline("Далі", b'next_2')
]


next_3 = [
    button.inline("Почати путь за луком", b'go_to_bow')
]