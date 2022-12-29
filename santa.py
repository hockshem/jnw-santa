# the os module helps us access environment variables
# i.e., our API keys
import os
from dotenv import load_dotenv

# the Discord Python API
import discord
import logging

from discord.ext import tasks, commands 
from discord.ext import menus

from wish import add_to_prize_pool, update_prize_pool, get_prize_name
from member_points import increase_pts, get_pts_bal, get_leaderboard, get_pts_acc
from leaderboard_menu import LeaderboardPageSource
from santa_utils import send_event_embed, create_prize_pool_embed

load_dotenv()
token = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

client = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    await send_event_embed(client)

@client.check
def check_team_permission(ctx):
    return ctx.author.get_role(939912652237463612) is not None

@client.command()
async def give(ctx, pts: int, *members: discord.Member):
    ids = []
    for member in members: 
        increase_pts(member.id, pts)
        ids.append(f"<@{member.id}>")
    recipients = ', '.join(ids)
    await ctx.send(f"{recipients} received `{pts} $JNW`!")

@client.command(name="giveroles")
async def give(ctx, pts: int, *roles: discord.Role):
    ids = []
    for role in roles:
        role_members = role.members
        for member in role_members:
            increase_pts(member.id, pts)
            ids.append(f"<@{member.id}>")
    recipients = ', '.join(ids)
    await ctx.send(f"{recipients} received `{pts} $JNW`!")

@client.command()
async def balance(ctx, member: discord.Member):
    bal = get_pts_bal(member.id)
    await ctx.send(f"{member.name} has `{bal} $JNW`!")

@client.command()
async def spent(ctx, member: discord.Member):
    acc = get_pts_acc(member.id)
    bal =  get_pts_bal(member.id)
    spent = acc - bal
    await ctx.send(f"{member.name} has spent `{spent} $JNW`!")

@client.command()
async def prizepool(ctx):
    prize_pool_embed = create_prize_pool_embed()
    await ctx.send(embed=prize_pool_embed, ephemeral=True)

@client.command()
async def additem(ctx, tier, item_name, total_amount, contributor, twitter): 
    add_to_prize_pool(int(tier), item_name, int(total_amount), contributor, twitter)
    await ctx.send(f"Successfully added {item_name} x{total_amount} into the Tier {tier} prize pool.", ephemeral=True)

@client.command()
async def update(ctx, item_id, change):
    update_prize_pool(item_id, int(change))
    await ctx.send(f"Successfully updated the amount of item {item_id}: {get_prize_name(item_id)}!")

@client.command()
async def leaderboard(ctx):
    (data, total_pts) = get_leaderboard()
    formatter = LeaderboardPageSource(data, total_pts=total_pts)
    menu = menus.MenuPages(formatter, delete_message_after=True)
    await menu.start(ctx)

client.run(token, log_handler=handler)