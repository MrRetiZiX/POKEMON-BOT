import telebot
import random
import datetime
from config import token
from telebot import types
from logic import Pokemon, Wizard, Fighter

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Получить покемона")
    btn2 = types.KeyboardButton("Мой покемон")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
                     "Привет! Я бот для игры с покемонами. Выбери действие:", 
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Получить покемона")
def get_pokemon(message):
    username = message.from_user.username
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Волшебник")
    btn2 = types.KeyboardButton("Боец")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, 
                     "Выбери класс своего покемона:", 
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Волшебник", "Боец"])
def create_pokemon(message):
    username = message.from_user.username
    pokemon_class = message.text
    
    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    rarity = random.choice(rarities)
    
    if pokemon_class == "Волшебник":
        pokemon = Wizard(username, rarity)
    else:
        pokemon = Fighter(username, rarity)
    
    bot.send_photo(message.chat.id, pokemon.show_img(), caption=f"Ты получил покемона редкости {rarity}!\n{pokemon.info()}")
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Мой покемон")
    btn2 = types.KeyboardButton("Атаковать")
    btn3 = types.KeyboardButton("Лечить")
    btn4 = types.KeyboardButton("Кормить")
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, "Что будешь делать дальше?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Мой покемон")
def show_pokemon(message):
    username = message.from_user.username
    
    if username in Pokemon.pokemons:
        pokemon = Pokemon.pokemons[username]
        bot.send_photo(message.chat.id, pokemon.show_img(), caption=pokemon.info())
    else:
        bot.send_message(message.chat.id, "У тебя еще нет покемона. Нажми 'Получить покемона'")

@bot.message_handler(func=lambda message: message.text == "Атаковать")
def attack_menu(message):
    username = message.from_user.username
    
    if username not in Pokemon.pokemons:
        bot.send_message(message.chat.id, "У тебя еще нет покемона. Нажми 'Получить покемона'")
        return
    
    opponents = [user for user in Pokemon.pokemons.keys() if user != username]
    
    if not opponents:
        bot.send_message(message.chat.id, "Нет других тренеров для сражения")
        return
    
    markup = types.InlineKeyboardMarkup()
    for opponent in opponents:
        markup.add(types.InlineKeyboardButton(
            text=f"@{opponent} ({Pokemon.pokemons[opponent].name})", 
            callback_data=f"attack_{opponent}"
        ))
    
    bot.send_message(message.chat.id, "Выбери противника для атаки:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('attack_'))
def attack_pokemon(call):
    attacker_username = call.from_user.username
    defender_username = call.data.split('_')[1]
    
    if attacker_username in Pokemon.pokemons and defender_username in Pokemon.pokemons:
        attacker = Pokemon.pokemons[attacker_username]
        defender = Pokemon.pokemons[defender_username]
        
        result = attacker.attack(defender)
        bot.send_message(call.message.chat.id, result)
    else:
        bot.send_message(call.message.chat.id, "Ошибка: один из покемонов не найден")

@bot.message_handler(func=lambda message: message.text == "Лечить")
def heal_pokemon(message):
    username = message.from_user.username
    
    if username in Pokemon.pokemons:
        pokemon = Pokemon.pokemons[username]
        result = pokemon.heal()
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "У тебя еще нет покемона. Нажми 'Получить покемона'")

@bot.message_handler(func=lambda message: message.text == "Кормить")
def feed_pokemon(message):
    username = message.from_user.username
    
    if username in Pokemon.pokemons:
        pokemon = Pokemon.pokemons[username]
        result = pokemon.feed()
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "У тебя еще нет покемона. Нажми 'Получить покемона'")

if __name__ == "__main__":
    bot.polling(none_stop=True)
