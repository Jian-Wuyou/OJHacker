import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.embeds import Embeds
from utils.config import Config

# Load .env and initialize environment variables
load_dotenv()

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*Config.command_prefixes),
    case_insensitive=True,
    intents=intents
)


@bot.event
async def on_message(msg: discord.Message):
    await bot.process_commands(msg)


@bot.event
async def on_ready():
    # Remove default help command
    bot.remove_command("help")

    # Load select cogs in folder /cogs
    cogs_to_load = ['Generators', 'ReplitDatabase', 'Testcases']
    for cog_name in cogs_to_load:
        try:
            bot.load_extension(f'cogs.{cog_name}')
            print(f"Loaded: cogs.{cog_name}")
        except (commands.ExtensionFailed, commands.NoEntryPointError) as e:
            print(f"There was an issue while loading cogs.{cog_name}.")
            print(e)

    print(f'{bot.user} has connected to Discord!')

    print('Available commands:', [i.name for i in bot.commands])
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="!start")
    )


@bot.command(aliases=['cogs', 'cog', 'extensions'])
async def extension(ctx: commands.context.Context, option, ext=None):
    """Reload, load, or unload extensions.

    - Usage: <command-prefix> extension <option> <cog's name>
    - <option> : list, load, unload, reload
    - Only allowable if user is adminUser.
    """

    # Check if user is in admin_users
    if ctx.author.id not in Config.admin_users:
        await ctx.send(f"You do not have permission to {option} extensions.")
        return

    if option == "list":
        await ctx.send(f"Loaded extensions: `{', '.join(bot.cogs.keys())}`")
        return

    try:
        if option == "reload":
            bot.reload_extension(f"cogs.{ext}")
        elif option == "load":
            bot.load_extension(f"cogs.{ext}")
        elif option == "unload":
            bot.unload_extension(f"cogs.{ext}")

        # Prompt usage method if option is wrong
        else:
            await ctx.send(
                f"Usage: `{Config.command_prefix[0]}extension <option> <extension>`\n"
                "Options: `list, load, unload, reload`"
            )
            return

    except (commands.ExtensionFailed, commands.NoEntryPointError) as e:
        await ctx.send(f"There was an issue with loading the `{ext}` extension.")
        print(e)
        return
    except commands.ExtensionNotFound as e:
        await ctx.send(f"The `{ext}` extension does not exist.")
        print(e)
        return
    except commands.ExtensionAlreadyLoaded as e:
        await ctx.send(f"The `{ext}` extension is already loaded.")
        print(e)
        return
    except commands.ExtensionNotLoaded as e:
        await ctx.send(f"The `{ext}` extension is not yet loaded.")
        print(e)
        return

    # Success message
    print(f'Loaded: cogs.{ext}')
    await ctx.send(f"{ext} extension {option}ed.")


if __name__ == "__main__":
    bot.run(TOKEN)
