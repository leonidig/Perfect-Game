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

without_heal = [
    button.inline("Некст", b'road_to_bow')
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


action_guild_1 = [
    button.inline("Взаємодіяти з гільдією", b'action_guild_1')
]


third_question = [
    [button.inline("issubclass", b'q3_false_1')],
    [button.inline("classof()", b'q3_false_2')],
    [button.inline("isinstance", b'q3_true')],
    [button.inline("type()", b'q3_false_1')],
]


enter_3 = [
    button.inline("Йти далі", b'enter_3')
]


enter_4 = [
    button.inline("Вперед", b'enter_4')
]


quest_for_npc = [
    button.inline("Звідки ти про мене стільки знаєш", b'quest_for_npc')
]


enter_5 = [
    button.inline("Йти далі", b'enter_5')
]


heal_before_fight = [
    [button.inline("Випити хілку", b'use_heal')]
]

third_fight = [
    [button.inline("Битися", b'fight_3')]
]


do_hit = [
    button.inline("Удар!", b'do_hit')
]


walk = [
    [button.inline("Йти за луком", b'walk_to_bow')],
    [button.inline("Йти назад", b'back')]
]

however_walk = [
    [button.inline("Йти за луком", b'walk_to_bow')]
]


open_test = [
    button.inline("Пройти тест", b'open_test')
]


question_four = [
    [button.inline('True', b'q4_true')],
    [button.inline('False', b'g4_false_1')],
    [button.inline('None', b'g4_false_2')],
    [button.inline('Error', b'g4_false_3')],
]

next_question1 = [
    [button.inline("Наступне Запитання", b'next_question1')]
]

question_five = [
    [button.inline("dict_values([3, 4, 5, 6])", b"q5_false_1")],
    [button.inline("dict_values([2, 3, 4, 5])", b"q5_true")],
    [button.inline("KeyError", b"q5_false_2")],
    [button.inline("dict_values([0, 1, 2, 3, 4])", b"q5_false_3")]
]

next_question2 = [
    [button.inline("Наступне Запитання", b'next_question2')]
]


question_six = [
    [button.inline("97, 98, 99, 100, 101", b"q6_false_1")],
    [button.inline("97, 98, 99, 100, 101, 102", b"q6_false_2")],
    [button.inline("abcde", b"q6_true")],
    [button.inline("['a', 'b', 'c', 'd', 'e']", b"q6_false_3")]
]



run = [
    button.inline("Йти далі 🚪 🔑", b'run')
]

run1 = [
    button.inline("Зайти в ворота", b'open_door')
]


get_bow = [
    button.inline("ЗАБРАТИ", b'get_bow')
]


go_home = [
    button.inline("Йти до бази гільдії 🏯", b'go_home')
]

kill_bat = [
    button.inline("Стрільнути", b'kill_bat')
]


comeback_to_guild = [
    button.inline("Вперед", b'comeback_to_guild')
]


thx = [
    button.inline("Дякую", b'thx')
]


for_guard = [
    button.inline("Що мені зробити?", b'for_guard')
]


aisle_question = [
    [button.inline("2", b'q7_false_1')],
    [button.inline("6", b'q7_false_2')],
    [button.inline("8", b'q7_true')],
    [button.inline("KeyError", b'q7_false_3')]

]


meet_enchanter = [
    button.inline("Пройти до зачарувальника", b'meet_enchanter')
]


enchanter_choice = [
    [button.inline("Купити", b'buy')],
    [button.inline("В мене є", b'have_fire')]
]

buy = [
    [button.inline("Купити", b'buy')]
]


return_to_base = [
    button.inline("Йти на базу", b'return_to_base')
]


visit_shop = [
    button.inline("Гуляти по базі", b'visit_shop')
]

shop = [
    [button.inline("Королівська запіканка (12 коп + 10 хп)", b'shop_zapikanka')],
    [button.inline("Каша бідняка з медом (5 коп + 4 хп)", b'shop_kasha')],
    [button.inline("Гарячий хліб з часниковим маслом (8 коп + 9 хп)", b'shop_hleb')],
    [button.inline("Крем-суп з гарбуза та моркви (15 коп + 14 хп)", b'shop_soup')],
    [button.inline("Запечена свинина з лісовими грибами (22 коп + 17 хп)", b'shop_svinina')],
]


stroll = [
    button.inline("Ходити по базі гільдії", b'stroll')
]


help_npc = [
    [button.inline("Допомогти", b'help')],
    [button.inline("Ігнорувати", b"ignore")]
]


go_hunting = [
    button.inline("Йти полювати", b'go_hunting')
]


hit_the_boar = [
    button.inline("Стріляти", b'hit_the_boar')
]

walk_in_forest = [
    button.inline("Йти далі", b'walk_in_forest')
]

second_hit = [
    button.inline("Стріляю!", b'second_hit')
]