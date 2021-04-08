import discord
from discord.ext import commands

class Solutions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

def setup(bot: commands.Bot):
    bot.add_cog(Solutions(bot))