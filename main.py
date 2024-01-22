from discord.ext import commands
import random

bot = commands.Bot(command_prefix='!')


def generate_weapons():
    weapons = [
        "M416", "AKM", "Kar98k", "UMP45", "SCAR-L",
        "Vector", "SKS", "Mini14", "S12K", "AWM"
    ]
    return weapons


def generate_inventory():
    inventory = {}
    weapons = generate_weapons()

    inventory["weapon_1"] = random.choice(weapons)
    inventory["weapon_2"] = random.choice(weapons)
    inventory["swap_item"] = random.choice(["затиск", "пристрій", "голограма"])
    inventory["swap_item_quantity"] = random.randint(0, 10)

    return inventory


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='generate_inventory', help='Generate PUBG inventory for a player')
async def generate_inventory_command(ctx, *players):
    for player in players:
        inventory_player = generate_inventory()
        inventory_message = (
            f"\nІм'я гравця: {player}\n"
            f"Зброя 1: {inventory_player['weapon_1']}\n"
            f"Зброя 2: {inventory_player['weapon_2']}\n"
            f"Предмет для свапу: {inventory_player['swap_item']} "
            f"(Кількість: {inventory_player['swap_item_quantity']})"
        )
        await ctx.send(inventory_message)


@bot.command(name='change_weapon', help='Change a weapon slot for a player')
async def change_weapon_command(ctx, player, slot):
    inventory_player = generate_inventory()
    current_weapon = inventory_player[f'weapon_{slot}']
    new_weapon = random.choice(generate_weapons())
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


bot.run('YOUR_BOT_TOKEN')
