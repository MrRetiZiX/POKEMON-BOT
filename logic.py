import random
import requests
from io import BytesIO
import datetime

class Pokemon:
    pokemons = {}
    
    def __init__(self, username, rarity="Common"):
        
        self.username = username
        self.rarity = rarity
        self.pokemon_trainer = username
        
        rarity_multipliers = {
            "Common": 1.0,
            "Uncommon": 1.2,
            "Rare": 1.5,
            "Epic": 2.0,
            "Legendary": 3.0
        }
        
        multiplier = rarity_multipliers[rarity]
        
        pokemon_id = random.randint(1, 151)
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
        pokemon_data = response.json()
        
        self.name = pokemon_data["name"].capitalize()
        self.img_url = pokemon_data["sprites"]["other"]["official-artwork"]["front_default"]
        
        self.hp = int(pokemon_data["stats"][0]["base_stat"] * multiplier)
        self.attack = int(pokemon_data["stats"][1]["base_stat"] * multiplier)
        self.defense = int(pokemon_data["stats"][2]["base_stat"] * multiplier)
        self.speed = int(pokemon_data["stats"][5]["base_stat"] * multiplier)
        
        self.power = random.randint(10, 30)
        self.wins = 0
        
        Pokemon.pokemons[username] = self
    
    def info(self):
        return f"Имя: {self.name}\nHP: {self.hp}\nСила: {self.power}\nАтака: {self.attack}\nЗащита: {self.defense}\nСкорость: {self.speed}"
    
    def show_img(self):
        response = requests.get(self.img_url)
        return BytesIO(response.content)
    
    def attack(self, enemy):
        if isinstance(enemy, Wizard):
            chance = random.randint(1, 5)
            if chance == 1:
                return f"Покемон-волшебник @{enemy.pokemon_trainer} применил щит в сражении с @{self.pokemon_trainer}"
        
        if enemy.hp > self.power:
            enemy.hp -= self.power
            return f"Сражение @{self.pokemon_trainer} с @{enemy.pokemon_trainer}"
        else:
            enemy.hp = 0
            self.wins += 1
            return f"Победа @{self.pokemon_trainer} над @{enemy.pokemon_trainer}!"
    
    def heal(self, amount=None):
        if amount is None:
            amount = int(self.hp * 0.3)
        
        self.hp += amount
        return f"Покемон {self.name} восстановил {amount} HP"

    def feed(self, feed_interval=20, hp_increase=10):
        current_time = datetime.datetime.now()
        delta_time = datetime.timedelta(hours=feed_interval)
        
        if (current_time - self.last_feed_time) > delta_time:
            self.hp += hp_increase
            self.last_feed_time = current_time
            return f"Здоровье покемона увеличено. Текущее здоровье: {self.hp}"
        else:
            next_feed_time = self.last_feed_time + delta_time
            return f"Следующее время кормления покемона: {next_feed_time}"


class Wizard(Pokemon):
    def __init__(self, username, rarity="Common"):
        super().__init__(username, rarity)
        self.hp = int(self.hp * 1.5)
    
    def info(self):
        return f"У тебя покемон-волшебник\n{super().info()}"
    
    def attack(self, enemy):
        result = super().attack(enemy)
        
        if "Победа" in result:
            heal_amount = random.randint(5, 15)
            self.hp += heal_amount
            result += f"\nВолшебник восстановил {heal_amount} здоровья после победы!"
            
        return result


class Fighter(Pokemon):
    def __init__(self, username, rarity="Common"):
        super().__init__(username, rarity)
        self.power = int(self.power * 1.5)
    
    def info(self):
        return f"У тебя покемон-боец\n{super().info()}"
    
    def attack(self, enemy):
        super_power = random.randint(5, 15)
        self.power += super_power
        result = super().attack(enemy)
        self.power -= super_power
        
        if "Победа" in result:
            power_bonus = random.randint(1, 5)
            self.power += power_bonus
            result += f"\nБоец получил постоянный бонус к силе: +{power_bonus}!"
            
        return result + f"\nБоец применил супер-атаку силой: {super_power}"
