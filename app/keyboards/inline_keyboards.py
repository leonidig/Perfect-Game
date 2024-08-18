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