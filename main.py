import os
import PIL
import PIL.Image
import random
import sys
import telebot
import telebot.types as types
import threading
import time

from collections import Counter

help_str = '''
Dice Poker - your goal is to get the combination of dice throws that is higher by value that your opponent`s have. 
If you an your opponent have the same combination the winner is decided the highest dice value combination.
For example, a trio of fives of higher than a trio of fourth.'''

help_list_str = '''
	List of all combinations from lowest to highest:
	⚀⚁⚂⚃⚅ - high value
	⚁⚁⚃⚄⚅ - pair
	⚂⚂⚄⚄⚀ - two pairs
	⚂⚂⚂⚃⚄ - trio
	⚀⚁⚂⚃⚄ - five high straight
	⚁⚂⚃⚄⚅ - six high straight
	⚂⚂⚂⚄⚄ - full house
	⚃⚃⚃⚃⚀ - four of a king
	⚅⚅⚅⚅⚅ - five of a king
    '''

if __name__ == '__main__':
    bot = telebot.TeleBot(sys.argv[1])
else:
    sys.exit(0)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.set_my_commands(commands=[
        types.BotCommand('/new_game', description='Play new game'),
        types.BotCommand('/help', description='Print a help message')
    ])
    bot.send_message(message.chat.id, help_str)
    bot.send_message(message.chat.id, help_list_str)
    bot.send_message(message.chat.id, 'Pick an option from a menu:')

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, help_str)
    bot.send_message(message.chat.id, help_list_str)

@bot.message_handler(commands=['quit'])
def send_quit(message):
    bot.set_my_commands(commands=[
        types.BotCommand('/new_game', description='Play new game'),
        types.BotCommand('/help', description='Print a help message')
    ])

    if os.path.exists('files/%d' % message.chat.id):
        for f in os.listdir('files/%d' % message.chat.id):
            os.remove(os.path.join('files/%d' % message.chat.id, f))

        os.removedirs('files/%d' % message.chat.id)

    bot.send_message(message.chat.id, 'Pick an option from a menu:')

@bot.message_handler(commands=['new_game'])
def send_new_game_with_bot(message):
    bot.set_my_commands(commands=[
        types.BotCommand('/roll', description='Roll a dice'),
        types.BotCommand('/help', description='Print a help message'),
        types.BotCommand('/quit', description='Quit this game')
    ])

    bot.send_message(message.chat.id, 'Roll your dice:')

@bot.message_handler(commands=['roll'])
def send_new_game_with_bot(message):
    def inner():
        player_data   = []
        opponent_data = []

        player_img   = PIL.Image.new(mode='RGBA', size=(320, 64), color=(255, 255, 255))
        opponent_img = PIL.Image.new(mode='RGBA', size=(320, 64), color=(255, 255, 255))

        for i in range(5):
            player_data.append(random.randint(1, 6))
            opponent_data.append(random.randint(1, 6))

            player_dice_img = PIL.Image.open('./files/die-face-%d.png' % player_data[-1])
            opponent_dice_img = PIL.Image.open('./files/die-face-%d.png' % opponent_data[-1])

            player_img.paste(player_dice_img, (64 * i, 0))
            opponent_img.paste(opponent_dice_img, (64 * i, 0))
        
        player_combination, opponent_combination, result = define_winner(player_data, opponent_data)

        os.makedirs('files/%d' % message.chat.id, exist_ok=True)

        player_img.save('files/%d/player.png' % message.chat.id)
        opponent_img.save('files/%d/opponent.png' % message.chat.id)

        bot.send_photo(message.chat.id, types.InputFile(file='files/%d/player.png' % message.chat.id))
        bot.send_message(message.chat.id, 'Player`s roll - %s.' % player_combination)

        time.sleep(1)

        bot.send_photo(message.chat.id, types.InputFile(file='files/%d/opponent.png' % message.chat.id))
        bot.send_message(message.chat.id, 'Opponent`s roll - %s.' % opponent_combination)

        time.sleep(1)

        if result < 0:
            bot.send_message(message.chat.id, 'Opponent wins!')
        elif result > 0:
            bot.send_message(message.chat.id, 'Player wins!')
        else:
            bot.send_message(message.chat.id, 'Draw!')

        time.sleep(1)
        bot.send_message(message.chat.id, 'Roll your dice:')

    threading.Thread(target=inner).start()

def define_winner(player_data, opponent_data):
    def is_five_in_a_row(data):
        if all(map(lambda item: item == data[0], data)):
            return (data[0], )
        
        return False

    def is_four_in_a_row(data):
        counted = dict(map(lambda item: item[::-1], Counter(data).items()))

        if 4 in counted:
            return (counted[4], )
        
        return False

    def is_full_house(data):
        counted = dict(map(lambda item: item[::-1], Counter(data).items()))

        if 3 in counted and 2 in counted:
            return counted[3], counted[2]

        return False

    def is_straight(data):
        min_value = min(data)

        for i, v in enumerate(sorted(data)):
            if v + i != min_value + i:
                return False
            
        return (max(data), )

    def is_three(data):
        counted = dict(map(lambda item: item[::-1], Counter(data).items()))

        if 3 in counted:
            return (counted[3], )

        return False

    def is_two_pairs(data):
        one_pair_found = False
        first_value = None

        for k, v in Counter(data).items():
            if v == 2:
                if one_pair_found:
                    return first_value, k
                
                one_pair_found = True
                first_value = k

        return False

    def is_pair(data):
        counted = dict(map(lambda item: item[::-1], Counter(data).items()))

        if 2 in counted:
            return (counted[2], )

        return False
    
    variants = (
        ('five in a row', is_five_in_a_row, lambda x: x + 74),
        ('four in a row', is_four_in_a_row, lambda x: x + 68),
        ('full house', is_full_house, lambda x, y: x * 3 + y * 2 + 35),
        ('straight', is_straight, lambda x: x + 29),
        ('tree', is_three, lambda x: x + 23),
        ('two pairs', is_two_pairs, lambda x, y: x + y + 12),
        ('pair', is_pair, lambda x: x + 6),
        ('high value', lambda data: (max(data), ), lambda x: x),
    )

    player_score   = 0
    opponent_score = 0

    player_combination   = None
    opponent_combination = None

    for name, filter_func, score_func in variants:
        r1 = filter_func(player_data)
        r2 = filter_func(opponent_data)

        if r1 and player_score == 0:
            player_score = score_func(*r1)
            player_combination = name

        if r2 and opponent_score == 0:
            opponent_score = score_func(*r2)
            opponent_combination = name

        if not (player_score == 0 or opponent_score == 0):
            break

    if player_score < opponent_score:
        return (player_combination, opponent_combination, -1)
    
    if player_score > opponent_score:
        return (player_combination, opponent_combination, 1)

    return (player_combination, opponent_combination, 0)

bot.infinity_polling()
