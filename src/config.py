from os import path

import discord
from discord.ext import commands

class Config:
    def __init__(self):
        self.command_prefixes: list[str]
        self.admin_users: set[int]
        self.admin_roles: dict[int, set[int]]
        self.allowed_guilds: set[int]

        self.command_prefixes = ['!', '$']

        self.base_path = path.dirname(path.realpath(__file__))

        self.admin_users = {
            546398120960065547  # Jian
        }

        self.admin_roles = {
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

        self.allowed_guilds = set(self.admin_roles.keys())

    def is_allowed_admin_commands(self):
        async def predicate(ctx: commands.Context):
            if ctx.author.id in self.admin_users:
                return True
            if not isinstance(ctx.channel, discord.TextChannel):
                return False
            if ctx.guild.id not in self.allowed_guilds:
                return False
            has_admin_role = commands.has_any_role(*self.admin_roles[ctx.guild.id]).predicate
            return await has_admin_role(ctx)
        return commands.check(predicate)
