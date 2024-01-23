from pymongo.mongo_client import MongoClient
from discord.ext import commands
from dotenv import dotenv_values
import discord
import random
import json

config = dotenv_values(".env")

intents = discord.Intents.all()
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


def generate_new_inventory():
    first_weapon = random.choice(weapons)
    second_weapon = random.choice(weapons)
    drop_weapon = random.choice(drop_weapons)

    if first_weapon is second_weapon:
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
        f"Зброя 'дропова': **{inventory_player['drop_weapon']}**\n"
        f"Предмет для свапу: **{inventory_player['swap_item']}** \n"
        f"(Кількість: {inventory_player['swap_item_quantity']})"
    )


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')


@bot.hybrid_command(name='generate_inventory', description='Generate PUBG inventory for a player')
async def generate_inventory(ctx, players: str) -> None:
    message = ''
    for player in players.split(','):
        inventory_player = generate_new_inventory()
        message += get_inventory_message(player, inventory_player)

        preset_data = {'player': player, 'inventory': inventory_player}
        oldUser = presets_collection.find_one({'player': player})
        if oldUser is not None:
            presets_collection.update_one(
                {'player': player},
                {'$set': {'inventory': inventory_player}}
            )
            print(f"Updated inventory for {player} ({inventory_player['weapon_1']}, {inventory_player['weapon_2']})")
        else:
            presets_collection.insert_one(preset_data)
            print(f"Created new inventory for {player} ({inventory_player['weapon_1']}, {inventory_player['weapon_2']})")
    await ctx.send(message)


@bot.hybrid_command(name='change_weapon', description='Change a weapon slot for a player')
async def change_weapon(ctx, player: str, slot: int) -> None:
    default_inventory = presets_collection.find_one({'player': player})['inventory']
    inventory_player = generate_new_inventory()
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
        print(f"Changed weapon for {player} from {current_weapon} to {new_weapon}\n")
    else:
        await ctx.send(f"Зміни оружія не було, користувача не знайдено! Згенеровано новий інвентар")
        presets_collection.insert_one({'player': player, 'inventory': inventory_player})
        print(
            f"Created new inventory for {player} from cw func ({inventory_player['weapon_1']}, {inventory_player['weapon_2']})\n")
    await ctx.send(get_inventory_message(player, inventory_player))

    if default_inventory is not None:
        presets_collection.update_one({'player': player}, {'$set': {'inventory': inventory_player}})


@bot.hybrid_command(name='clear_inventory', description='Clear inventory by usernames')
async def clear_inventory(ctx, players: str) -> None:
    presets_collection.delete_many({'player': players.split(',')})
    await ctx.send(f"Інвентар/і очищено успішно!")


bot.run(config['BOT_KEY'])
