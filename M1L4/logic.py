import random
from PIL import Image
import requests
from io import BytesIO

class Pokemon:
    pokemons = {}
    
    def __init__(self, username, rarity="Common"):
        self.username = username
        self.rarity = rarity
        
        # Множители характеристик в зависимости от редкости
        rarity_multipliers = {
            "Common": 1.0,
            "Uncommon": 1.2,
            "Rare": 1.5,
            "Epic": 2.0,
            "Legendary": 3.0
        }
        
        multiplier = rarity_multipliers[rarity]
        
        # Генерация случайного покемона (ID от 1 до 151 - первое поколение)
        pokemon_id = random.randint(1, 151)
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
        pokemon_data = response.json()
        
        self.name = pokemon_data["name"].capitalize()
        self.img_url = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        
        # Базовые характеристики, умноженные на множитель редкости
        self.hp = int(pokemon_data["stats"][0]["base_stat"] * multiplier)
        self.attack = int(pokemon_data["stats"][1]["base_stat"] * multiplier)
        self.defense = int(pokemon_data["stats"][2]["base_stat"] * multiplier)
        self.speed = int(pokemon_data["stats"][5]["base_stat"] * multiplier)
        
        Pokemon.pokemons[username] = self
    
    def info(self):
        return f"Имя: {self.name}\nHP: {self.hp}\nАтака: {self.attack}\nЗащита: {self.defense}\nСкорость: {self.speed}"
    
    def show_img(self):
        response = requests.get(self.img_url)
        return BytesIO(response.content)
class BattleAI:
    def __init__(self, difficulty="Medium"):
        self.difficulty = difficulty
        # Создаем случайного покемона для ИИ
        self.pokemon = Pokemon(f"AI_{random.randint(1000, 9999)}", 
                              rarity=self.get_rarity_by_difficulty())
    
    def get_rarity_by_difficulty(self):
        """Определяет редкость покемона в зависимости от сложности"""
        if self.difficulty == "Easy":
            rarities = ["Common", "Uncommon"]
            weights = [0.7, 0.3]
        elif self.difficulty == "Medium":
            rarities = ["Common", "Uncommon", "Rare"]
            weights = [0.4, 0.4, 0.2]
        else:  # Hard
            rarities = ["Uncommon", "Rare", "Epic", "Legendary"]
            weights = [0.4, 0.3, 0.2, 0.1]
        
        return random.choices(rarities, weights=weights)[0]
    
    def make_move(self, turn):
        """
        Выбирает действие AI в бою
        Возвращает: (действие, урон)
        """
        # Базовый урон зависит от атаки покемона
        base_damage = max(5, self.pokemon.attack // 10)
        
        # Увеличиваем сложность с каждым ходом для Hard режима
        if self.difficulty == "Hard" and turn > 3:
            base_damage = int(base_damage * 1.2)
        
        # Выбор действия зависит от сложности
        if self.difficulty == "Easy":
            actions = ["Атака", "Защита", "Спец. атака"]
            weights = [0.6, 0.3, 0.1]
        elif self.difficulty == "Medium":
            actions = ["Атака", "Защита", "Спец. атака"]
            weights = [0.5, 0.3, 0.2]
        else:  # Hard
            actions = ["Атака", "Защита", "Спец. атака"]
            weights = [0.4, 0.2, 0.4]
        
        action = random.choices(actions, weights=weights)[0]
        
        # Расчет урона в зависимости от действия
        if action == "Атака":
            damage = base_damage
        elif action == "Защита":
            # При защите наносит меньше урона, но получает меньше урона в ответ
            damage = base_damage // 2
        else:  # Спец. атака
            # Спец. атака может нанести больше урона, но может и промахнуться
            if random.random() < 0.7:  # 70% шанс попадания
                damage = base_damage * 2
            else:
                damage = 0
                action = "Спец. атака (промах)"
        
        # Добавляем случайность в урон
        damage_variation = random.uniform(0.8, 1.2)
        damage = int(damage * damage_variation)
        
        # Для Easy режима ограничиваем максимальный урон
        if self.difficulty == "Easy":
            damage = min(damage, 15)
        
        return action, damage
    
    def get_reward(self):
        """Возвращает награду за победу над этим AI"""
        base_reward = 50
        
        if self.difficulty == "Easy":
            multiplier = 1
        elif self.difficulty == "Medium":
            multiplier = 2
        else:  # Hard
            multiplier = 3
        
        # Дополнительный бонус за редкость покемона
        rarity_bonus = {
            "Common": 0,
            "Uncommon": 20,
            "Rare": 50,
            "Epic": 100,
            "Legendary": 200
        }
        
        total_reward = base_reward * multiplier + rarity_bonus[self.pokemon.rarity]
        # Добавляем небольшую случайность
        return total_reward + random.randint(-20, 20)