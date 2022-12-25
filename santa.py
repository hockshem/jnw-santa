# the os module helps us access environment variables
# i.e., our API keys
import os
from dotenv import load_dotenv

# the Discord Python API
import discord
import logging

from discord.ui import View, Button
from discord.ext import tasks, commands 

from wish import standard_wish, premium_wish, view_prize_pool, add_to_prize_pool, update_prize_pool, get_prize_name
from member_points import increase_pts, get_pts_bal, claim_daily

load_dotenv()
token = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    await send_event_embed()

@client.check
def check_team_permission(ctx):
    return ctx.author.get_role(939912652237463612) is not None

@client.command()
async def test(ctx, arg):
    await ctx.send(arg)

@client.command()
async def give(ctx, pts: int, *members: discord.Member):
    ids = []
    for member in members: 
        increase_pts(member.id, pts)
        ids.append(f"<@{member.id}>")
    recipients = ', '.join(ids)
    await ctx.send(f"{recipients} received {str(pts)} points!")

@client.command()
async def balance(ctx, member: discord.Member):
    bal = get_pts_bal(member.id)
    await ctx.send(f"{member.name} has {str(bal)} points!")

@client.command()
async def prizepool(ctx):
    prize_pool_dict = view_prize_pool()

    prize_pool_embed = discord.Embed(title="Prize Pool")
    
    prize_id_str = ""
    prize_name_str = ""
    remaining_str = ""
    total_prizes = 0

    for _, prizes in prize_pool_dict.items():
        for prize in prizes: 
            prize_id, prize_name, remaining = prize
            total_prizes += int(remaining)
            prize_id_str += f"{prize_id}\n"
            prize_name_str += f"{prize_name}\n"
            remaining_str += f"{remaining}\n"

    prize_pool_embed.add_field(name="Prize ID", value=prize_id_str, inline=True)
    prize_pool_embed.add_field(name="Prize Name", value=prize_name_str, inline=True)
    prize_pool_embed.add_field(name="Remaining", value=remaining_str, inline=True)

    prize_pool_embed.set_footer(text=f"Total: {total_prizes}")

    await ctx.send(embed=prize_pool_embed, ephemeral=True)


@client.command()
async def additem(ctx, tier, item_name, total_amount, contributor_id=""): 
    add_to_prize_pool(int(tier), item_name, total_amount, contributor_id)
    await ctx.send(f"Successfully added {item_name} x{total_amount} into the Tier {tier} prize pool.", ephemeral=True)

@client.command()
async def update(ctx, item_id, change):
    update_prize_pool(item_id, change)
    await ctx.send(f"Successfully updated the amount of item {item_id}: {get_prize_name(item_id)}!")
    

async def send_event_embed():
    # get the test channel 
    test_channel = client.get_channel(1055319238149144576)
    # TODO: add checking and not resend the event embed if it already exists
    title = "Test Embed"
    desc = "Test Description"
    
    event_embed = discord.Embed(title=title, description=desc)

    image_url = "./graphics/gacha.jpeg"
    file = discord.File(image_url, filename="gacha.jpeg")

    component_view = View()

    wish_button = Button()
    wish_button.label = 'Wish'
    wish_button.custom_id = 'wish'
    wish_button.callback = send_wish_details

    bal_button = Button()
    bal_button.label = 'Balance'
    bal_button.custom_id = 'balance'
    bal_button.callback = send_balance

    daily_button = Button()
    daily_button.label = 'Daily'
    daily_button.custom_id = 'daily'
    daily_button.callback = claim

    component_view.add_item(wish_button)
    component_view.add_item(bal_button)
    component_view.add_item(daily_button)

    event_embed.set_image(url="attachment://gacha.jpeg")

    await test_channel.send(file=file, embed=event_embed, view=component_view)

async def send_balance(interaction):
    bal = get_pts_bal(interaction.user.id)
    await interaction.response.send_message(f"You have {str(bal)} points!", ephemeral=True)

async def send_wish_details(interaction):
    title = "Choose type of wish"
    desc = "Normal Wish and Advanced Wish"
    wish_details_embed = discord.Embed(title=title, description=desc)

    std_wish_button = Button()
    std_wish_button.label = 'Standard Wish'
    std_wish_button.emoji = '🎩'
    std_wish_button.custom_id = 'stdwish'
    std_wish_button.callback = std_wish

    prm_wish_button = Button()
    prm_wish_button.label = 'Premium Wish'
    prm_wish_button.style = discord.ButtonStyle.primary
    prm_wish_button.emoji = '👑'
    prm_wish_button.custom_id = 'prmwish'
    prm_wish_button.callback = prm_wish

    component_view = View()
    component_view.add_item(std_wish_button)
    component_view.add_item(prm_wish_button)

    await interaction.response.send_message(embed=wish_details_embed, view=component_view, ephemeral=True)

async def std_wish(interaction):
    member = interaction.user
    roles = [role.id for role in member.roles]
    result = standard_wish(member.id, roles)
    result_message = ""

    if result is None: 
        result_message = f"{member.name}, you don't have enough balance or the required role to use that wish."
    else: 
        prize = result["Prize Name"]
        if prize.lower() == "nothing":
            result_message = f"Sorry, <@{member.id}>, you won nothing! Better luck next time!"
        else: 
            result_message = f"Congratulations! <@{member.id}>, you have won {prize} x1!"
    
    await interaction.response.send_message(result_message, ephemeral=True)

async def prm_wish(interaction):
    member = interaction.user
    roles = [role.id for role in member.roles]
    result = premium_wish(member.id, roles)
    result_message = ""

    if result is None: 
        result_message = f"{member.name}, you don't have enough balance or the required role to use that wish."
    else: 
        prize = result["Prize Name"]
        result_message = f"Congratulations! <@{member.id}>, you have won {prize} x1!"

    await interaction.response.send_message(result_message, ephemeral=True)

async def claim(interaction):
    member = interaction.user
    claim_result = claim_daily(member.id)
    status = claim_result["status"]
    points = claim_result["points"]

    result_message = ""

    if status:
        result_message = f"<@{member.id}>, you claimed ${points} successfully!"
    else:
        result_message = f"<@{member.id}>, you just claimed today! Come back tomorrow!"
    
    await interaction.response.send_message(result_message, ephemeral=True)

client.run(token, log_handler=handler)