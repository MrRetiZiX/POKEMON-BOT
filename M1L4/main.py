import telebot 
from config import token
import time
from logic import Pokemon, BattleAI
import random
from telebot import types
import datetime

bot = telebot.TeleBot(token) 

POKEMON_EMOJI = "🔥 🌊 🌿 ⚡ 🦋 🐉 🌟 💫 🔮 🎮"
RARITY_SYMBOLS = {
    "Common": "⚪",
    "Uncommon": "🟢",
    "Rare": "🔵",
    "Epic": "🟣",
    "Legendary": "🟠"
}

POKEMON_PRICES = {
    "Common": 100,
    "Uncommon": 300,
    "Rare": 800,
    "Epic": 2000,
    "Legendary": 5000
}

user_balance = {}
daily_rewards = {}
active_battles = {}

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
{POKEMON_EMOJI}
*Добро пожаловать в мир покемонов!*
Здесь ты можешь поймать своего уникального покемона.

Команды:
/go - поймать покемона
/info - информация о твоем покемоне
/battle - сразиться с диким покемоном
/shop - магазин предметов
/sell - продать своего покемона
/balance - проверить баланс
/daily - получить ежедневную награду
{POKEMON_EMOJI}
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    
    if message.from_user.username not in user_balance:
        user_balance[message.from_user.username] = 500
        bot.send_message(message.chat.id, "💰 Вы получили 500 монет для начала приключения!")

@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.username not in Pokemon.pokemons.keys():
        search_msg = bot.send_message(message.chat.id, "🔍 Начинаем поиск покемона...")
        time.sleep(1)
        bot.edit_message_text("🔍 Ищем покемона в высокой траве...", message.chat.id, search_msg.message_id)
        time.sleep(1)
        bot.edit_message_text("👀 Кто-то шевелится в кустах!", message.chat.id, search_msg.message_id)
        time.sleep(1)
        
        rarity_roll = random.random()
        if rarity_roll < 0.50:
            rarity = "Common"
        elif rarity_roll < 0.80:
            rarity = "Uncommon"
        elif rarity_roll < 0.95:
            rarity = "Rare"
        elif rarity_roll < 0.99:
            rarity = "Epic"
        else:
            rarity = "Legendary"
            
        pokemon = Pokemon(message.from_user.username, rarity=rarity)
        
        bot.edit_message_text(f"✨ Вы нашли покемона! ✨", message.chat.id, search_msg.message_id)
        
        info_text = f"""
{RARITY_SYMBOLS[rarity]} *{pokemon.name}* {RARITY_SYMBOLS[rarity]}
━━━━━━━━━━━━━━━━━━━━
📊 *Характеристики*:
❤️ HP: {pokemon.hp}
⚔️ Атака: {pokemon.attack}
🛡️ Защита: {pokemon.defense}
🏃 Скорость: {pokemon.speed}
━━━━━━━━━━━━━━━━━━━━
✨ *Редкость*: {rarity}
🔍 *Тренер*: @{message.from_user.username}
        """
        
        bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "🚫 Ты уже создал себе покемона! Береги его!")

@bot.message_handler(commands=['info'])
def info(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        pokemon = Pokemon.pokemons[message.from_user.username]
        
        rarity = getattr(pokemon, 'rarity', "Common")
        
        info_text = f"""
{RARITY_SYMBOLS[rarity]} *{pokemon.name}* {RARITY_SYMBOLS[rarity]}
━━━━━━━━━━━━━━━━━━━━
📊 *Характеристики*:
❤️ HP: {pokemon.hp}
⚔️ Атака: {pokemon.attack}
🛡️ Защита: {pokemon.defense}
🏃 Скорость: {pokemon.speed}
━━━━━━━━━━━━━━━━━━━━
✨ *Редкость*: {rarity}
🔍 *Тренер*: @{message.from_user.username}
💰 *Стоимость*: {POKEMON_PRICES[rarity]} монет
        """
        
        bot.send_message(message.chat.id, info_text, parse_mode="Markdown")
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "❌ У тебя еще нет покемона! Используй /go чтобы поймать своего первого покемона.")

@bot.message_handler(commands=['battle'])
def battle(message):
    username = message.from_user.username
    if username not in Pokemon.pokemons.keys():
        bot.reply_to(message, "❌ У тебя нет покемона для битвы! Используй /go чтобы поймать покемона.")
        return
    
    player_pokemon = Pokemon.pokemons[username]
    
    ai_difficulty = random.choice(["Easy", "Medium", "Hard"])
    ai_opponent = BattleAI(difficulty=ai_difficulty)
    
    battle_msg = bot.send_message(message.chat.id, f"🔍 Ищем дикого покемона для битвы...")
    time.sleep(1)
    bot.edit_message_text(f"⚡ Найден дикий покемон: *{ai_opponent.pokemon.name}*!", 
                         message.chat.id, battle_msg.message_id, parse_mode="Markdown")
    
    bot.send_photo(message.chat.id, ai_opponent.pokemon.show_img(), 
                  caption=f"Дикий {ai_opponent.pokemon.name} (Сложность: {ai_difficulty})")
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    attack_btn = types.InlineKeyboardButton("⚔️ Атака", callback_data=f"battle_attack_{username}")
    special_btn = types.InlineKeyboardButton("🔥 Спец. атака", callback_data=f"battle_special_{username}")
    defense_btn = types.InlineKeyboardButton("🛡️ Защита", callback_data=f"battle_defense_{username}")
    run_btn = types.InlineKeyboardButton("🏃 Убежать", callback_data=f"battle_run_{username}")
    
    markup.add(attack_btn, special_btn)
    markup.add(defense_btn, run_btn)
    
    battle_info = {
        "player": player_pokemon,
        "ai": ai_opponent,
        "player_hp": player_pokemon.hp,
        "ai_hp": ai_opponent.pokemon.hp,
        "turn": 1
    }
    
    active_battles[username] = battle_info
    
    battle_text = f"""
⚔️ *Битва начинается!* ⚔️
━━━━━━━━━━━━━━━━━━━━
Твой {player_pokemon.name}: ❤️ {battle_info['player_hp']}
Дикий {ai_opponent.pokemon.name}: ❤️ {battle_info['ai_hp']}
━━━━━━━━━━━━━━━━━━━━
Выбери свое действие:
    """
    
    bot.send_message(message.chat.id, battle_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('battle_'))
def battle_callback(call):
    action, username = call.data.split('_')[1], call.data.split('_')[2]
    
    if username not in active_battles:
        bot.answer_callback_query(call.id, "Эта битва уже завершена!")
        return
    
    battle_info = active_battles[username]
    player_pokemon = battle_info["player"]
    ai_opponent = battle_info["ai"]
    
    player_damage = 0
    player_defense = 0
    
    if action == "attack":
        player_damage = max(5, player_pokemon.attack // 10)
        battle_info["ai_hp"] -= player_damage
        bot.answer_callback_query(call.id, f"Ты нанес {player_damage} урона!")
    
    elif action == "special":
        if random.random() < 0.7:
            player_damage = max(10, player_pokemon.attack // 5)
            battle_info["ai_hp"] -= player_damage
            bot.answer_callback_query(call.id, f"Мощная атака! Ты нанес {player_damage} урона!")
        else:
            bot.answer_callback_query(call.id, "Твоя специальная атака промахнулась!")
    
    elif action == "defense":
        player_defense = max(5, player_pokemon.defense // 10)
        bot.answer_callback_query(call.id, f"Ты усилил защиту на {player_defense}!")
    
    elif action == "run":
        bot.answer_callback_query(call.id, "Ты сбежал с поля боя!")
        bot.edit_message_text("🏃‍♂️ Ты сбежал с поля боя! Битва окончена.", 
                             call.message.chat.id, call.message.message_id)
        del active_battles[username]
        return
    
    ai_action, ai_damage = ai_opponent.make_move(battle_info["turn"])
    
    if player_defense > 0:
        ai_damage = max(0, ai_damage - player_defense)
    
    battle_info["player_hp"] -= ai_damage
    
    battle_info["turn"] += 1
    
    if battle_info["ai_hp"] <= 0:
        reward = random.randint(50, 200)
        user_balance[username] = user_balance.get(username, 0) + reward
        
        victory_text = f"""
🎉 *Победа!* 🎉
━━━━━━━━━━━━━━━━━━━━
Твой {player_pokemon.name} победил дикого {ai_opponent.pokemon.name}!
💰 Награда: {reward} монет
━━━━━━━━━━━━━━━━━━━━
        """
        
        bot.edit_message_text(victory_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        
        stat_boost = random.randint(1, 3)
        stat_type = random.choice(["hp", "attack", "defense", "speed"])
        
        if stat_type == "hp":
            player_pokemon.hp += stat_boost
            boost_msg = f"❤️ HP твоего покемона увеличился на {stat_boost}!"
        elif stat_type == "attack":
            player_pokemon.attack += stat_boost
            boost_msg = f"⚔️ Атака твоего покемона увеличилась на {stat_boost}!"
        elif stat_type == "defense":
            player_pokemon.defense += stat_boost
            boost_msg = f"🛡️ Защита твоего покемона увеличилась на {stat_boost}!"
        else:
            player_pokemon.speed += stat_boost
            boost_msg = f"🏃 Скорость твоего покемона увеличилась на {stat_boost}!"
        
        bot.send_message(call.message.chat.id, boost_msg)
        
        del active_battles[username]
        return
    
    elif battle_info["player_hp"] <= 0:
        defeat_text = f"""
😢 *Поражение!* 😢
━━━━━━━━━━━━━━━━━━━━
Твой {player_pokemon.name} проиграл дикому {ai_opponent.pokemon.name}!
Твой покемон ослаблен, но скоро восстановится.
━━━━━━━━━━━━━━━━━━━━
        """
        
        bot.edit_message_text(defeat_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
        del active_battles[username]
        return
    
    battle_text = f"""
⚔️ *Битва продолжается!* ⚔️
━━━━━━━━━━━━━━━━━━━━
Твой {player_pokemon.name}: ❤️ {battle_info['player_hp']}
Дикий {ai_opponent.pokemon.name}: ❤️ {battle_info['ai_hp']}
━━━━━━━━━━━━━━━━━━━━
Ход {battle_info['turn']}:
• Ты использовал: {action.capitalize()}
• Противник использовал: {ai_action}
• Ты нанес: {player_damage} урона
• Противник нанес: {ai_damage} урона
━━━━━━━━━━━━━━━━━━━━
Выбери свое действие:
    """
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    attack_btn = types.InlineKeyboardButton("⚔️ Атака", callback_data=f"battle_attack_{username}")
    special_btn = types.InlineKeyboardButton("🔥 Спец. атака", callback_data=f"battle_special_{username}")
    defense_btn = types.InlineKeyboardButton("🛡️ Защита", callback_data=f"battle_defense_{username}")
    run_btn = types.InlineKeyboardButton("🏃 Убежать", callback_data=f"battle_run_{username}")
    
    markup.add(attack_btn, special_btn)
    markup.add(defense_btn, run_btn)
    
    bot.edit_message_text(battle_text, call.message.chat.id, call.message.message_id, 
                         reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['shop'])
def shop(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for rarity, price in POKEMON_PRICES.items():
        btn = types.InlineKeyboardButton(f"{RARITY_SYMBOLS[rarity]} {rarity} покемон - {price} монет", 
                                        callback_data=f"buy_{rarity}")
        markup.add(btn)
    
    shop_text = """
💰 *Магазин покемонов* 💰
━━━━━━━━━━━━━━━━━━━━
Здесь вы можете купить нового покемона.
Выберите редкость покемона для покупки:
    """
    
    bot.send_message(message.chat.id, shop_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_pokemon(call):
    rarity = call.data.split('_')[1]
    username = call.from_user.username
    price = POKEMON_PRICES[rarity]
    
    if username in Pokemon.pokemons:
        bot.answer_callback_query(call.id, "У вас уже есть покемон! Сначала продайте его через /sell")
        return
    
    if username not in user_balance:
        user_balance[username] = 0
    
    if user_balance[username] < price:
        bot.answer_callback_query(call.id, f"Недостаточно монет! Нужно {price}, у вас {user_balance[username]}")
        return
    
    user_balance[username] -= price
    
    pokemon = Pokemon(username, rarity=rarity)
    
    bot.answer_callback_query(call.id, f"Вы купили {rarity} покемона {pokemon.name}!")
    
    info_text = f"""
✅ *Покупка успешна!* ✅
{RARITY_SYMBOLS[rarity]} *{pokemon.name}* {RARITY_SYMBOLS[rarity]}
━━━━━━━━━━━━━━━━━━━━
📊 *Характеристики*:
❤️ HP: {pokemon.hp}
⚔️ Атака: {pokemon.attack}
🛡️ Защита: {pokemon.defense}
🏃 Скорость: {pokemon.speed}
━━━━━━━━━━━━━━━━━━━━
✨ *Редкость*: {rarity}
💰 *Потрачено*: {price} монет
💰 *Остаток*: {user_balance[username]} монет
    """
    
    bot.edit_message_text(info_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")
    bot.send_photo(call.message.chat.id, pokemon.show_img())

@bot.message_handler(commands=['sell'])
def sell_pokemon(message):
    username = message.from_user.username
    
    if username not in Pokemon.pokemons:
        bot.reply_to(message, "❌ У вас нет покемона для продажи!")
        return
    
    pokemon = Pokemon.pokemons[username]
    rarity = getattr(pokemon, 'rarity', "Common")
    price = POKEMON_PRICES[rarity]
    
    sell_price = int(price * random.uniform(0.7, 0.9))
    
    markup = types.InlineKeyboardMarkup()
    confirm_btn = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"sell_confirm_{sell_price}")
    cancel_btn = types.InlineKeyboardButton("❌ Отмена", callback_data="sell_cancel")
    markup.add(confirm_btn, cancel_btn)
    
    sell_text = f"""
💰 *Продажа покемона* 💰
━━━━━━━━━━━━━━━━━━━━
Вы собираетесь продать своего покемона:
{RARITY_SYMBOLS[rarity]} *{pokemon.name}* ({rarity})

💰 Цена продажи: {sell_price} монет

⚠️ Внимание! Это действие нельзя отменить после подтверждения!
    """
    
    bot.send_message(message.chat.id, sell_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('sell_'))
def sell_pokemon_callback(call):
    action = call.data.split('_')[1]
    username = call.from_user.username
    
    if action == "cancel":
        bot.answer_callback_query(call.id, "Продажа отменена")
        bot.edit_message_text("❌ Продажа отменена", call.message.chat.id, call.message.message_id)
        return
    
    if action == "confirm":
        if username not in Pokemon.pokemons:
            bot.answer_callback_query(call.id, "У вас нет покемона для продажи!")
            return
        
        sell_price = int(call.data.split('_')[2])
        pokemon_name = Pokemon.pokemons[username].name
        
        if username not in user_balance:
            user_balance[username] = 0
        user_balance[username] += sell_price
        
        del Pokemon.pokemons[username]
        
        bot.answer_callback_query(call.id, f"Вы продали {pokemon_name} за {sell_price} монет!")
        
        sell_text = f"""
✅ *Продажа успешна!* ✅
━━━━━━━━━━━━━━━━━━━━
Вы продали покемона {pokemon_name} за {sell_price} монет.
💰 Ваш баланс: {user_balance[username]} монет

Используйте /go чтобы поймать нового покемона или
/shop чтобы купить покемона в магазине.
        """
        
        bot.edit_message_text(sell_text, call.message.chat.id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['balance'])
def check_balance(message):
    username = message.from_user.username
    
    if username not in user_balance:
        user_balance[username] = 0
    
    balance_text = f"""
💰 *Ваш баланс* 💰
━━━━━━━━━━━━━━━━━━━━
У вас {user_balance[username]} монет

Способы заработка:
• Победа в битвах (/battle)
• Ежедневная награда (/daily)
• Продажа покемонов (/sell)
    """
    
    bot.send_message(message.chat.id, balance_text, parse_mode="Markdown")

@bot.message_handler(commands=['daily'])
def daily_reward(message):
    username = message.from_user.username
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if username in daily_rewards and daily_rewards[username] == current_date:
        time_until_tomorrow = (datetime.datetime.now().replace(hour=0, minute=0, second=0) + 
                              datetime.timedelta(days=1) - datetime.datetime.now())
        hours, remainder = divmod(time_until_tomorrow.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        bot.reply_to(message, 
                    f"⏳ Вы уже получили ежедневную награду сегодня!\nСледующая награда будет доступна через {hours} ч {minutes} мин")
        return
    
    reward = random.randint(100, 300)
    
    streak = 1
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if username in daily_rewards and daily_rewards[username] == yesterday:
        streak = 2
        reward = int(reward * 1.5)
    
    if username not in user_balance:
        user_balance[username] = 0
    user_balance[username] += reward
    
    daily_rewards[username] = current_date
    
    reward_text = f"""
🎁 *Ежедневная награда!* 🎁
━━━━━━━━━━━━━━━━━━━━
Вы получили {reward} монет!
{f"🔥 Бонус за серию дней: x1.5!" if streak > 1 else ""}
💰 Ваш баланс: {user_balance[username]} монет

Возвращайтесь завтра за новой наградой!
    """
    
    bot.send_message(message.chat.id, reward_text, parse_mode="Markdown")

if __name__ == "__main__":
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    bot.polling(none_stop=True, interval=0)