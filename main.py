from pymongo.mongo_client import MongoClient
from discord.ext import commands
from dotenv import dotenv_values
import discord
import random
import json

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

weapons = json.load(open('./weapons.json', encoding='utf-8'))
drop_weapons = json.load(open('./drop_weapons.json', encoding='utf-8'))
swap_items = json.load(open('./swap_items.json', encoding='utf-8'))

client = MongoClient(config['MONGODB_CONNECT_URL'])

presets_collection = client['pubg_inventory']['presets']


def generate_swap_item():
    swap_item = random.choice(swap_items)
    swap_item_quantity = random.randint(1, swap_item[1])
    return [swap_item[0], swap_item_quantity]


def generate_inventory():
    first_weapon = random.choice(weapons)
    second_weapon = random.choice(weapons)
    drop_weapon = random.choice(drop_weapons)

    if second_weapon is second_weapon:
        second_weapon = random.choice(weapons)

    if drop_weapon is [first_weapon, second_weapon]:
        drop_weapon = random.choice(drop_weapons)

    swap_item = generate_swap_item()

    return {
        "weapon_1": first_weapon,
        "weapon_2": second_weapon,
        "drop_weapon": drop_weapon,
        "swap_item": swap_item[0],
        "swap_item_quantity": swap_item[1]
    }


def get_inventory_message(player, inventory_player):
    return (
        f"\n ```Ім'я гравця: {player}```\n"
        f"Зброя 1: **{inventory_player['weapon_1']}**\n"
        f"Зброя 2: **{inventory_player['weapon_2']}**\n"
        f"Зброя, яку дозволено для свапу з дропу: **{inventory_player['drop_weapon']}**\n"
        f"Предмет для свапу: **{inventory_player['swap_item']}** "
        f"(Кількість: {inventory_player['swap_item_quantity']})\n \n"
    )


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='gi', help='Generate PUBG inventory for a player')
async def generate_inventory_command(ctx, players):
    message = ''
    for player in players.split(','):
        inventory_player = generate_inventory()
        message.join(get_inventory_message(player, inventory_player))

        preset_data = {'player': player, 'inventory': inventory_player}
        oldUser = presets_collection.find_one({'player': player})
        if oldUser is not None:
            presets_collection.update_one(
                {'player': player},
                {'$set': {'inventory': inventory_player}}
            )
        else:
            presets_collection.insert_one(preset_data)
    await ctx.send(message)


@bot.command(name='cw', help='Change a weapon slot for a player')
async def change_weapon_command(ctx, player, slot):
    default_inventory = presets_collection.find_one({'player': player})['inventory']
    inventory_player = generate_inventory()
    if default_inventory is not None:
        inventory_player = default_inventory
    current_weapon = inventory_player[f'weapon_{slot}']
    new_weapon = random.choice(weapons)
    inventory_player[f'weapon_{slot}'] = new_weapon

    swap_item = generate_swap_item()
    inventory_player['swap_item'] = swap_item[0]
    inventory_player['swap_item_quantity'] = swap_item[1]

    if default_inventory is not None:
        await ctx.send(
            f"Оружіе для **{player}** у слоті {slot} було змінено з ~~{current_weapon}~~ на **{new_weapon}**")
    else:
        await ctx.send(f"Зміни оружія не було, користувача не знайдено!")
    await ctx.send(get_inventory_message(player, inventory_player))

    presets_collection.update_one({'player': player}, {'$set': {'inventory': inventory_player}})


@bot.command(name='ci', help='Clear inventory by username')
async def change_weapon_command(ctx, player):
    presets_collection.delete_one({'player': player})
    await ctx.send(f"Інвентар очищено успішно!")


bot.run(config['BOT_KEY'])
