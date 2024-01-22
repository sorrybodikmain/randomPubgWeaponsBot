import discord
from discord.ext import commands
from discord_slash import SlashCommand
from pymongo import MongoClient
import random
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

slash = SlashCommand(bot)

weapons = json.load(open('./weapons.json', encoding='utf-8'))

swap_items = json.load(open('./swap_items.json', encoding='utf-8'))

# Підключення до MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['pubg_inventory']
presets_collection = db['presets']


def generate_inventory():
    inventory = {}

    inventory["weapon_1"] = random.choice(weapons)
    inventory["weapon_2"] = random.choice(weapons)
    inventory["swap_item"] = random.choice(["затиск", "пристрій", "голограма"])
    inventory["swap_item_quantity"] = random.randint(0, 10)

    return inventory


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


# Створення інвентарю та збереження його в MongoDB для кожного гравця
@slash.slash(name='generate_inventory', description='Generate PUBG inventory for players')
async def generate_inventory_command(ctx, players: commands.Param(str, desc="List of players")):
    for player in players.split():
        inventory_player = generate_inventory()
        inventory_message = (
            f"\nІм'я гравця: {player}\n"
            f"Зброя 1: {inventory_player['weapon_1']}\n"
            f"Зброя 2: {inventory_player['weapon_2']}\n"
            f"Предмет для свапу: {inventory_player['swap_item']} "
            f"(Кількість: {inventory_player['swap_item_quantity']})"
        )
        await ctx.send(inventory_message)

        # Збереження пресету в MongoDB
        preset_data = {
            'player': player,
            'inventory': inventory_player
        }
        presets_collection.insert_one(preset_data)


# Зміна одного слоту зброї та оновлення пресету в MongoDB
@slash.slash(name='change_weapon', description='Change a weapon slot for a player')
async def change_weapon_command(ctx, player: commands.Param(str, desc="Player's name"),
                                slot: commands.Param(int, desc="Weapon slot (1 or 2)")):
    inventory_player = generate_inventory()
    current_weapon = inventory_player[f'weapon_{slot}']
    new_weapon = random.choice(weapons)
    inventory_player[f'weapon_{slot}'] = new_weapon
    inventory_message = (
        f"\nІм'я гравця: {player}\n"
        f"Зброя 1: {inventory_player['weapon_1']}\n"
        f"Зброя 2: {inventory_player['weapon_2']}\n"
        f"Предмет для свапу: {inventory_player['swap_item']} "
        f"(Кількість: {inventory_player['swap_item_quantity']})"
    )
    await ctx.send(f"Оружіе для {player} у слоті {slot} було змінено з {current_weapon} на {new_weapon}")
    await ctx.send(inventory_message)

    presets_collection.update_one({'player': player}, {'$set': {'inventory': inventory_player}})


bot.run('MTE5ODkzMDY3NDE4NzUxMzk2OA.GS7j9c.IDL8sM_Pywe4qxBoEgCdXI8qy0bISDWT-BGguA')
