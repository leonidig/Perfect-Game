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

only_heal = [
    button.inline("Випити 🧪", b'use_heal')
]

choice_damage = [
    button.inline("🎲", b'choice_damage')
]
start_gight = [
    button.inline("Почати Битву", b'start_gight')
]

first_hit = [
    button.inline("Вдaрити!", b"first_hit")
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

go_4 = [
    [button.inline("Почати путь", b'go_4')]
]

go_to_merchant = [
    [button.inline("Поговорити з торговцем", b'dialog_with_merchant')]
]
merchant_choice = [
    [button.inline("Продати ( +20 🪙)", b'do_trade')],
    [button.inline("Йти далі", b'go_5')]
]


go_6 = [
    button.inline("Залишити табір", b'go_6')
]


go_7 = [
    button.inline("Йти по лісу", b'go_7')
]


start_gight_2 = [
    button.inline("Вдарити!", b'kick_2')
]


send_dice = [
    button.inline("🎲", b'dice')
]


next_8 = [
    button.inline("Далі", b'next_8')
]

hit = [
    button.inline("Бити", b'hit')
]

final_attack_2 = [
        [button.inline("Бий монстра", b'do_attack')]
]


enter_1 = [
    [button.inline("Використати(+15 хп)", b'use_heal')],
    [button.inline("Вперед за луком!!!", b'road_to_bow')]
]


second_question = [
    [button.inline("[1, 4, 9]", b'q2_false_1')],
    [button.inline("[2, 3, 4]", b'q2_false_1')],
    [button.inline("[1, 2, 3, 4, 5, 6]", b'q2_false_1')],
    [button.inline("[2, 4, 6]", b'q2_true')]
]


enter_2 = [
    button.inline("В путь", b'enter_2')
]


guild_choice = [
    [button.inline("Орден Місячного Зілля", b"guild_mages")],
    [button.inline("Легіон Вогняного Молота", b"guild_fighters")],
    [button.inline("Орден Місячного Зілля", b"guild_trackers")],
]