from discord.ext import commands
import random

bot = commands.Bot(command_prefix='!')

weapons = [
    # Штурмові гвинтівки
    "M16A4",
    "M416",
    "SCAR-L",
    "G36C",
    "QBZ95",
    "AK-47",
    "Honey Badger",
    "AUG",
    # Марксманські гвинтівки
    "SKS",
    "Mk14 EBR",
    "SLR",
    "VSS",
    "Mini14",
    # Снайперські гвинтівки
    "M24",
    "AWM",
    "Kar98K",
    # Пістолети-кулемети
    "Vector",
    "UMP9",
    "MP5K",
    "PP-19 Bizon",
    "Tommy Gun",
    # Пістолети
    "P92",
    "P1911",
    "R1895",
    "Deagle",
    "Glock 18",
    # Озброєння ближнього бою
    "Sawed-off",
    "Double Barrel",
    "Machete",
    "Pan",
    # Метальна зброя
    "Crossbow",
    "Flare Gun",
    # Інше
    "Throwables",
]

swap_items = [
    "Шолом 1",
    "Шолом 2",
    "Шолом 3",
    "Жилет",
    "Жилет 1",
    "Жилет 2",
    "Жилет 3",
    # Медичні приналежності
    "Пакет першої допомоги",
    "Медичний набір",
    "Таблетки від болю",
    "Енергетичний напій",
    # Інше
    "Димна граната",
    "Молотов коктейль",
    "С4",
    "Граната з удушаючим газом",
    "Коробка з повітрям",
]


def generate_inventory():
    inventory = {}

    inventory["weapon_1"] = random.choice(weapons)
    inventory["weapon_2"] = random.choice(weapons)
    inventory["swap_item"] = random.choice(swap_items)
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


bot.run('YOUR_BOT_TOKEN')
