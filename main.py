import configparser
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load .env and initialize environment variables
load_dotenv()

# Load config.ini
currentPath = os.path.dirname(os.path.realpath(__file__))
configs = configparser.ConfigParser()
configs.read(currentPath + "/config.ini")

parsed_config = {
    'admin_users' : set(int(i) for i in configs["General"]["adminUsers"].split(',')),
    'allowed_guilds' : set(int(i) for i in configs["General"]["allowedGuilds"].split(',')),
    'command_prefix' : [i.strip() for i in configs["General"]["commandPrefix"].split(',')]
}

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(*['!']),
    case_insensitive=True,
    intents=intents
)

loaded_cogs = []

@bot.event
async def on_message(msg: discord.Message):
    await bot.process_commands(msg)


@bot.event
async def on_ready():
    # Remove default help command
    bot.remove_command("help")

    # Load select cogs in folder /cogs
    cogs_to_load = ['Config', 'Generators']
    for cog_name in cogs_to_load:
        try:
            bot.load_extension(f'cogs.{cog_name}')
            loaded_cogs.append(cog_name)
            print(f"Loaded cog: cogs.{cog_name}")
        except (commands.ExtensionFailed, commands.NoEntryPointError):
            print(f"There was an issue while loading cogs.{cog_name}.")

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

    # Check if user is in adminUsers
    if ctx.author.id not in admin_users:
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
                f"Usage: `{command_prefix[0]}extension <option> <extension>`\n"
                "Options: `list, load, unload, reload`"
            )
            return

    except (commands.ExtensionFailed, commands.NoEntryPointError):
        await ctx.send(f"There was an issue with loading the `{ext}` extension.")
        return
    except commands.ExtensionNotFound:
        await ctx.send(f"The `{ext}` extension does not exist.")
        return
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f"The `{ext}` extension is already loaded.")
        return
    except commands.ExtensionNotLoaded:
        await ctx.send(f"The `{ext}` extension is not yet loaded.")
        return

    # Success message
    await ctx.send(f"{ext} extension {option.upper()}ED.")


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
