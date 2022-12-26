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

    for tier, prizes in prize_pool_dict.items():
        if tier == 3:
            break
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
async def additem(ctx, tier, item_name, total_amount, contributor, twitter): 
    add_to_prize_pool(int(tier), item_name, total_amount, contributor, twitter)
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

    component_view = View(timeout=None)

    wish_button = Button()
    wish_button.label = '许愿'
    wish_button.custom_id = 'wish'
    wish_button.emoji = '💫'
    wish_button.style = discord.ButtonStyle.primary
    wish_button.callback = send_wish_details

    bal_button = Button()
    bal_button.label = '查看余额'
    bal_button.custom_id = 'balance'
    bal_button.emoji = '💰'
    bal_button.callback = send_balance

    daily_button = Button()
    daily_button.label = '每日签到'
    daily_button.custom_id = 'daily'
    daily_button.emoji = '📆'
    daily_button.style = discord.ButtonStyle.success
    daily_button.callback = claim

    component_view.add_item(wish_button)
    component_view.add_item(bal_button)
    component_view.add_item(daily_button)

    event_embed.set_image(url="attachment://gacha.jpeg")

    await test_channel.send(file=file, embed=event_embed, view=component_view)

async def send_balance(interaction):
    user_id = interaction.user.id
    bal = get_pts_bal(interaction.user.id)
    await interaction.response.send_message(f"<@{user_id}>，你的余额为 ``{str(bal)} $JNW``。", ephemeral=True)

async def send_wish_details(interaction):
    title = "选择许愿类型"
    
    wish_details_embed = discord.Embed(title=title)
    wish_details_embed.add_field(name="普通许愿", value=f"""消耗: 100$JNW\n中奖概率：25% 落空、 65% 普通奖池奖品、10% 高级奖池奖品""", inline=False)
    wish_details_embed.add_field(name="高级许愿", value=f"""消耗: 300$JNW\n中奖概率：40% 普通奖池奖品、60% 高级奖池奖品""", inline=False)

    std_wish_button = Button()
    std_wish_button.label = '普通许愿'
    std_wish_button.emoji = '✨'
    std_wish_button.custom_id = 'stdwish'
    std_wish_button.callback = std_wish

    prm_wish_button = Button()
    prm_wish_button.label = '高级许愿'
    prm_wish_button.style = discord.ButtonStyle.primary
    prm_wish_button.emoji = '🌟'
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
        result_message = f"{member.name}, 您的 `$JNW` 余额不足！"
        await interaction.response.send_message(result_message, ephemeral=True)
        return
        
    await send_wish_result_embed(result, interaction.response)

async def prm_wish(interaction):
    member = interaction.user
    roles = [role.id for role in member.roles]
    result = premium_wish(member.id, roles)
    result_message = ""

    if result is None: 
        result_message = f"{member.name}, 您的 `$JNW` 余额不足！"
        await interaction.response.send_message(result_message, ephemeral=True)
        return
        
    await send_wish_result_embed(result, interaction.response)

async def send_wish_result_embed(result, response):
    directory = "./graphics/"

    luck_status = result["Status"]
    prize = result["Name"]
    twitter_link = result["Twitter"]
    image_name = result["Image"]
    contributor = result["Contributor"]

    if luck_status == -1:
        wish_result_embed = discord.Embed(title="抱歉！", description="很不幸地，你什么也没抽中！再接再厉！", colour=discord.Colour.red())
        wish_result_embed.set_image(url="https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif")
        await response.send_message(embed=wish_result_embed, ephemeral=True)
    else:
        colour = discord.Colour.green()
        if luck_status == 0:
            title="恭喜中奖！"
            desc = f"恭喜！🎉 你抽中了： \n- {prize} x1"

        elif luck_status == 1:
            title="欧运爆发！"
            desc = f"你太好运啦！🎉🎉🎉 你在幸运之神的眷顾下抽中了： \n- {prize} x1！"
        
        wish_result_embed = discord.Embed(title=title, description=desc, colour=colour)
        wish_result_embed.add_field(name="Twitter链接", value=twitter_link, inline=False)
        wish_result_embed.add_field(name="奖品提供", value=contributor)
        thumbnail_file = discord.File(f"{directory}{image_name}", filename=image_name)
        wish_result_embed.set_thumbnail(url=f"attachment://{image_name}")
        await response.send_message(file=thumbnail_file, embed=wish_result_embed, ephemeral=True)
    

async def claim(interaction):
    member = interaction.user
    claim_result = claim_daily(member.id)
    status = claim_result["status"]
    points = claim_result["points"]

    result_message = ""

    if status:
        result_message = f"<@{member.id}>, 签到成功！你获得了 `${points} $JNW`！"
    else:
        result_message = f"<@{member.id}>, 你今天已经签到过了哦，记得明日再来。"
    
    await interaction.response.send_message(result_message, ephemeral=True)

client.run(token, log_handler=handler)