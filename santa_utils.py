import discord
from discord.ui import View, Button
from wallet_submit import WalletSubmitForm

from member_points import get_pts_bal, claim_daily, increase_pts
from wish import standard_wish, premium_wish, get_prize_pool, get_wish_record

gacha_channel_id = 1056184573433761873
announcement_channel_id = 1056503133624356915

test_mode = False

if test_mode:
    gacha_channel_id = 1055319238149144576
    announcement_channel_id = 1056781667349569636

async def send_event_embed(client):
    # get the test channel 

    gacha_channel = client.get_channel(gacha_channel_id)

    last_message = await gacha_channel.fetch_message(gacha_channel.last_message_id)
    if last_message.author.id == client.user.id:
        await last_message.delete()

    # TODO: add checking and not resend the event embed if it already exists
    title = "Jer\'s 圣诞跨年扭蛋"
    desc = "璀璨的星星灯点亮web3世界，\n岁末狂欢派对集结号已经吹响！🎉\n\n快来参与各种活动取得 `$JNW` 来参加扭蛋吧！"
    
    event_embed = discord.Embed(title=title, description=desc)

    image_url = "./graphics/gacha.jpeg"
    file = discord.File(image_url, filename="gacha.jpeg")

    component_view = View(timeout=None)

    wish_button = Button()
    wish_button.label = '许愿'
    wish_button.custom_id = 'wish'
    wish_button.emoji = '💫'
    wish_button.style = discord.ButtonStyle.primary
    # wish_button.callback = send_wish_embed
    wish_button.disabled = True

    bal_button = Button()
    bal_button.label = '查看余额'
    bal_button.custom_id = 'balance'
    bal_button.emoji = '💰'
    # bal_button.callback = send_balance
    bal_button.disabled = True

    daily_button = Button()
    daily_button.label = '每日签到'
    daily_button.custom_id = 'daily'
    daily_button.emoji = '📆'
    daily_button.style = discord.ButtonStyle.success
    daily_button.disabled = True
    # daily_button.callback = claim

    # leaderboard_button = Button()
    # leaderboard_button.label = '排行榜'
    # leaderboard_button.custom_id = 'leaderboard'
    # leaderboard_button.emoji = '🏆'
    # leaderboard_button.style = discord.ButtonStyle.success
    # leaderboard_button.callback = leaderboard

    records_button = Button()
    records_button.label = '中奖记录'
    records_button.custom_id = 'records'
    records_button.emoji = '🎁'
    records_button.style = discord.ButtonStyle.success
    records_button.callback = create_wish_records_embed

    component_view.add_item(records_button)
    component_view.add_item(wish_button)
    component_view.add_item(bal_button)
    component_view.add_item(daily_button)
    # component_view.add_item(leaderboard_button)
    

    event_embed.set_image(url="attachment://gacha.jpeg")

    await gacha_channel.send(file=file, embed=event_embed, view=component_view)

def create_prize_pool_embed():
    prize_pool_dict = get_prize_pool()

    prize_pool_embed = discord.Embed(title="奖池")
    
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

    prize_pool_embed.add_field(name="ID", value=prize_id_str, inline=True)
    prize_pool_embed.add_field(name="奖品", value=prize_name_str, inline=True)
    prize_pool_embed.add_field(name="剩余数量", value=remaining_str, inline=True)

    prize_pool_embed.set_footer(text=f"总共数量：{total_prizes}")
    return prize_pool_embed

async def create_wish_records_embed(interaction):
    title = "中奖记录 🎁"

    member = interaction.user
    member_wish_records = get_wish_record(member.id)
    wish_records_embed = discord.Embed(title=title)

    submit_wallet_button = Button()
    submit_wallet_button.label = '提交钱包'
    submit_wallet_button.emoji = '🧧'
    submit_wallet_button.custom_id = 'submitwallet'
    # submit_wallet_button.callback = submit_wallet
    submit_wallet_button.disabled = True
    
    if len(member_wish_records) > 0:
        item_ids = ""
        item_names = ""
        
        for id, name in member_wish_records:
            item_ids += f"{id}\n"
            item_names += f"{name}\n"
        wish_records_embed.add_field(name="ID", value=item_ids)
        wish_records_embed.add_field(name="奖品名字", value=item_names)
    else:
        submit_wallet_button.disabled = True
        wish_records_embed.description = "无任何中奖记录"

    component_view = discord.ui.View()
    component_view.add_item(submit_wallet_button)

    await interaction.response.send_message(embed=wish_records_embed, view=component_view, ephemeral=True)

async def submit_wallet(interaction):
    await interaction.response.send_modal(WalletSubmitForm())

async def send_balance(interaction):
    user_id = interaction.user.id
    bal = get_pts_bal(interaction.user.id)
    await interaction.response.send_message(f"<@{user_id}>，你的余额为 `{bal} $JNW`。", ephemeral=True)

async def send_wish_embed(interaction):
    title = "选择许愿类型 💫"
    
    wish_details_embed = discord.Embed(title=title)
    wish_details_embed.add_field(name="普通许愿 ✨", value=f"""消耗: `100$JNW`\n中奖概率：25% 落空、 65% 普通奖池奖品、10% 高级奖池奖品""", inline=False)
    wish_details_embed.add_field(name="高级许愿 🌟", value=f"""消耗: `300$JNW`\n中奖概率：40% 普通奖池奖品、60% 高级奖池奖品""", inline=False)

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
        result_message = f"<@{member.id}>, 你的 `$JNW` 余额不足！"
        await interaction.response.send_message(result_message, ephemeral=True)
        return
        
    await send_wish_result_embed(result, interaction)

async def prm_wish(interaction):
    member = interaction.user
    roles = [role.id for role in member.roles]
    result = premium_wish(member.id, roles)
    result_message = ""

    if result is None: 
        result_message = f"<@{member.id}>, 你的 `$JNW` 余额不足！"
        await interaction.response.send_message(result_message, ephemeral=True)
        return
        
    await send_wish_result_embed(result, interaction)

async def send_wish_result_embed(result, interaction):
    directory = "./graphics/"

    luck_status = result["Status"] 
    prize = result["Name"]
    twitter_link = result["Twitter"] or "None"
    image_name = result["Image"]
    contributor = result["Contributor"] or "None"
    user_id = interaction.user.id 

    wish_announcement_channel = await interaction.guild.fetch_channel(announcement_channel_id)

    if luck_status == -1:
        refund_amt = 50
        wish_result_embed = discord.Embed(title="抱歉！", description=f"很不幸地，<@{user_id}> 什么也没抽中！但我们给你返还了 `{refund_amt} $JNW`，再接再厉！", colour=discord.Colour.red())
        increase_pts(user_id, refund_amt)
        wish_result_embed.set_image(url="https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif")
        await interaction.response.send_message(embed=wish_result_embed, ephemeral=True)        
        await wish_announcement_channel.send(embed=wish_result_embed)
    else:
        colour = discord.Colour.green()
        if luck_status == 0:
            title="恭喜中奖！"
            desc = f"恭喜！🎉 <@{user_id}> 抽中了： \n- {prize} x1"

        elif luck_status == 1:
            title="欧运爆发！"
            desc = f"<@{user_id}> 太好运啦！🎉🎉🎉 你在幸运之神的眷顾下抽中了： \n- {prize} x1！"
        
        wish_result_embed = discord.Embed(title=title, description=desc, colour=colour)
        wish_result_embed.add_field(name="Twitter链接", value=twitter_link, inline=False)
        wish_result_embed.add_field(name="奖品提供", value=contributor)
        
        if len(image_name) > 0:
            wish_thumbnail = discord.File(f"{directory}{image_name}", filename=f"wish_{image_name}")
            wish_result_embed.set_thumbnail(url=f"attachment://wish_{image_name}")
            await interaction.response.send_message(file=wish_thumbnail, embed=wish_result_embed, ephemeral=True)
            announcement_thumbnail = discord.File(f"{directory}{image_name}", filename=f"announcement_{image_name}")
            wish_result_embed.set_thumbnail(url=f"attachment://announcement_{image_name}")
            await wish_announcement_channel.send(file=announcement_thumbnail, embed=wish_result_embed)
        else:
            await interaction.response.send_message(embed=wish_result_embed, ephemeral=True)
            await wish_announcement_channel.send(embed=wish_result_embed)
        

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