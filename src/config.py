from os import path

import discord
from discord.ext import commands

class Config:
    command_prefixes: list[str]
    admin_users: set[int]
    admin_roles: dict[int, set[int]]
    allowed_guilds: set[int]

    command_prefixes = ['!', '$']

    base_path = path.dirname(path.realpath(__file__))

    admin_users = {
        546398120960065547  # Jian
    }

    admin_roles = {
        # barely survivng Discord Server
        769881233073111040: {
                770657966008696832,  # sadboi
                819800591672934430,  # Trinity
                781911338351198248   # Jotan's Angels
        },

        # Jian's Testing Server
        726417969122377738: {
                825679135941984266   # Admin
        }
    }

    allowed_guilds = set(admin_roles.keys())

    @staticmethod
    def is_allowed_admin_commands():
        async def predicate(ctx: commands.Context):
            if ctx.author.id in Config.admin_users:
                return True
            if not isinstance(ctx.channel, discord.TextChannel):
                return False
            if ctx.guild.id not in Config.allowed_guilds:
                return False
            has_admin_role = commands.has_any_role(*Config.admin_roles[ctx.guild.id]).predicate
            return await has_admin_role(ctx)
        return commands.check(predicate)
