import discord 
from discord.ext import menus

class LeaderboardPageSource(menus.ListPageSource):
    def __init__(self, entries, *, total_pts, per_page=10):
        super().__init__(entries, per_page=per_page)
        self.total_pts = total_pts 

    async def format_page(self, menu, page):
        leaderboard_embed = discord.Embed(title="排行榜 🏆")
        
        start = menu.current_page * self.per_page

        rank_str = ""
        members_str = ""
        acc_pts_str = ""

        for rank, (member, pts) in enumerate(page, start=start):
            rank += 1
            rank_str += f"{rank}\n"
            members_str += f"<@{member}>\n"
            acc_pts_str += f"{pts}\n"

        leaderboard_embed.add_field(name="排名", value=rank_str, inline=True)
        leaderboard_embed.add_field(name="成员", value=members_str, inline=True)
        leaderboard_embed.add_field(name="累计 $JNW", value=acc_pts_str, inline=True)
        leaderboard_embed.set_footer(text=f"总共 {self.total_pts} $JNW")
        
        return leaderboard_embed