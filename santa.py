# the os module helps us access environment variables
# i.e., our API keys
import os
from dotenv import load_dotenv

# the Discord Python API
import discord
import logging

from discord.ui import View, Button
from discord.ext import tasks, commands 

import random
from wish import standard_wish, premium_wish
from member_points import increase_pts, get_pts_bal

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
async def give(ctx, member: discord.Member, pts: int):
    increase_pts(member.id, pts)
    await ctx.send(f"{member.name} has successfully received {str(pts)} points!")

@client.command()
async def balance(ctx, member: discord.Member):
    bal = get_pts_bal(member.id)
    await ctx.send(f"{member.name} has {str(bal)} points!")

def claim_gift(user_id):
    # if not member has role 1049961153712889856, reject 
    pass

def get_emoji(type, n=[1, 1]):
    num = random.randint(n[0], n[1])
    # return [random.choice(reaction_emojis[type]) for _ in range(num)]
    return ['👌']

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

    # disabled_button = Button()
    # disabled_button.label = 'disabled'
    # disabled_button.custom_id = 'disabled'
    # disabled_button.disabled = True

    component_view.add_item(wish_button)
    component_view.add_item(bal_button)
    # component_view.add_item(disabled_button)

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
    std_wish_button.custom_id = 'stdwish'
    std_wish_button.callback = std_wish

    prm_wish_button = Button()
    prm_wish_button.label = 'Premium Wish'
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
            result_message = f"Sorry, {member.name}, you won nothing! Better luck next time!"
        else: 
            result_message = f"Congratulations! {member.name}, you have won {prize} x1!"
    
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
        result_message = f"Congratulations! {member.name}, you have won {prize} x1!"

    await interaction.response.send_message(result_message, ephemeral=True)

client.run(token, log_handler=handler)