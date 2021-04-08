import discord
from discord.ext import commands

class Config(commands.Cog):
    def __init__(self):
        """
        admin_roles
            format is {server_id: {role_ids}, ...}
        """
        self.admin_users: set[int]
        self.admin_roles: dict[int, set[int]]
        self.allowed_guilds: set[int]

        self.admin_users = {546398120960065547}
        self.admin_roles = {726417969122377738: {}}
        self.allowed_guilds = {726417969122377738}
    
    def is_allowed_admin_commands(self):
        def predicate(ctx: commands.Context):
            if ctx.author.id in self.admin_users:
                return True
            if not isinstance(ctx.guild.channel, discord.TextChannel):
                return False
            if ctx.guild.id not in self.allowed_guilds:
                return False
            has_admin_role = commands.has_any_role(self.admin_roles[ctx.guild.id]).predicate
            return await has_admin_role(ctx)
        return commands.check(predicate)