# main.py
import asyncio
import os

import discord
from discord.ext import commands

import auxi as aux
import constants as cnst
import generators as gen
import images
import testcases as tc

bot = commands.Bot(command_prefix="!")
client = discord.Client()

# =========== SHORTHAND COMMANDS =========== #
@bot.event
async def on_message(msg):
  class MiniContext:
    """
    A discord.ext.commands.context.Context but with only message and channel as atrbitutes
    """

    def __init__(self, x):
      self.message = x
      self.channel = x.channel

  if msg.content.startswith('!ptc'):
    try:
      msg.content = "!penge_tc" + msg.content[4:]
      ctx = MiniContext(msg)
      await penge_tc(ctx)
      return
    except Exception:
      print(f"Error at trying !pt\n{ctx}")
  elif msg.content.startswith('!pr'):
    try:
      msg.content = "!penge_random" + msg.content[3:]
      ctx = MiniContext(msg)
      await penge_random(ctx)
      return
    except Exception:
      print(f"Error at trying !pr\n{ctx}")
  elif msg.content.startswith('!skl'):
    try:
      msg.content = "!share_ko_lang" + msg.content[4:]
      ctx = MiniContext(msg)
      await share_ko_lang(ctx)
      return
    except Exception:
      print(f"Error at trying !skl\n{ctx}")
  elif msg.content.startswith('!it'):
    try:
      msg.content = "!insert_tc" + msg.content[3:]
      ctx = MiniContext(msg)
      await insert_tc(ctx)
      return
    except Exception:
      print(f"Error at trying !it\n{ctx}")
  elif msg.content.startswith('!tn'):
    try:
      msg.content = "!tcs_nga" + msg.content[3:]
      ctx = MiniContext(msg)
      await tcs_nga(ctx)
      return
    except Exception:
      print(f"Error at trying !tn\n{ctx}")

  await bot.process_commands(msg)


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!start"))


@bot.command()
async def join(ctx):
  channel = ctx.author.voice.channel
  await channel.connect()


@bot.command()
async def leave(ctx):
  await ctx.voice_client.disconnect()


@bot.command()
async def start(ctx):
  """Shows the instructions. Try it!"""
  msg = await ctx.channel.send(file=discord.File('hacker.png'))
  emojs = ['🧠', '👀', '🏆', '🥺', '🤟', '🎓']
  for zzz in emojs:
    await msg.add_reaction(zzz)
  await aux.show_instructions(ctx)


def non():
  return ("Cannot generate random test case. :((", "pogi si gab, pero hakdog.")


PARSERS = {
  "LE": [],
  "PA": [],
  "MP": [],
}

RANDOMERS = {
  "LE": [
    non,
    non,
    non,
    non,
    non,
    non,
    non,
    gen.genLE07,
    gen.genLE08,
    gen.genLE09
  ],
  "PA": [
    non,
    non,
    non,
    non,
    gen.genPA04,
    gen.genPA05,
    gen.genPA06
  ],
  "MP": [
    non,
    non
  ],
}

# ======= FOR INSERTING TEST CASES =========== #
@bot.command()
async def insert_tc(ctx):
  """Inserts a new test case into the system.

  Syntax:
    !insert_tc <LE/PA/MP><problem #> <test case label>
    !it <LE/PA/MP><problem #> <test case label>
  """

  msg = ctx.message.content
  auth = ctx.message.author

  inp = "".join(msg.split("!insert_tc ", 1)).split(maxsplit=1)

  is_ok, typ, idx, name = await aux.get_inputs(ctx, inp)

  if not is_ok:
    return

  await ctx.channel.send("Please enter your input (w/o formatting)")
  tc_input, _ = await aux.wait_response(bot, ctx, auth)

  await ctx.channel.send("Please enter your output (w/o formatting)")
  tc_output, _ = await aux.wait_response(bot, ctx, auth)

  confirm_msg = await ctx.channel.send("Upload the testcase? (thumbs up)")
  await confirm_msg.add_reaction(cnst.THUMBS_UP_EMOJI)

  tc_yes = await aux.wait_for_thumbs_up(ctx, bot)
  uid = tc.get_id()

  if tc_yes:
    tc.insert_testcase(uid, typ, idx, name, tc_input, tc_output)
    await ctx.channel.send(f"Testcase with UID {uid} added. Thanks!")
  else:
    await ctx.channel.send("Testcase ignored!")

# ======== PANG-DM NG TEST CASES ========= #
@bot.command()
async def penge_tc(ctx):
  """DMs all the stored test cases for a certain problem.

  Syntax:
    !penge_tc <LE/PA/MP><problem #>
    !ptc <LE/PA/MP><problem #>
  """

  msg = ctx.message.content
  author = ctx.message.author

  inp = "".join(msg.split("!penge_tc ", 1)).split(maxsplit=1)

  is_ok, typ, idx, name = await aux.get_inputs(ctx, inp)

  if not is_ok:
    return

  # retrieve test cases from db
  all_tc = tc.get_all(typ, idx)

  await author.create_dm()
  if not all_tc:
    await author.dm_channel.send("There are no testcases.")
  for tcs in all_tc:
    await aux.print_tc(ctx, typ, idx, tcs, author.dm_channel.send)
  try:
    await ctx.channel.send("DM SENT!")
  except Exception:
    await ctx["channel"].send("DM SENT!")

# ========= RANDOM GENERATOR ========== #
@bot.command()
async def penge_random(ctx):
  """DMs a randomly generated test case with the correct output.

  Syntax:
    !penge_random <LE/PA/MP><problem #>
    !pr <LE/PA/MP><problem #>
  """

  msg = ctx.message.content
  author = ctx.message.author

  inp = "".join(msg.split("!penge_random ", 1)).split(maxsplit=1)

  is_ok, typ, idx, name = await aux.get_inputs(ctx, inp)

  if not is_ok:
    return

  await author.create_dm()
  OJ_msg = "DM Sent!"
  rand, rand2 = non()
  try:
    f = RANDOMERS[typ][idx]
    tc, ans_tc = f()

    if tc:
      rand = "TEST CASE\n```python\n" + tc + "```"
    else:
      rand = "```There is no input generated```"
    if ans_tc:
      rand2 = "ANSWER\n```python\n" + ans_tc + "```"
    else:
      rand2 = "``` ```"
    if f == non:
      OJ_msg = "Sorry! There is no generator for that problem yet. Please contact the mods."
  except IndexError:
    print(f"Tried to create random for {typ}{idx}.")
    OJ_msg = "Sorry! There is no generator for that problem yet. Please contact the mods."
    rand, rand2 = non()

  await author.dm_channel.send(rand+"\n"+rand2)
  await ctx.channel.send(OJ_msg)

# ======== Share mo lang yung tc sa channel ====== #
@bot.command()
async def share_ko_lang(ctx, uid):
  """Sends the test case with a given UID.

  Syntax:
    !penge_random <uid>
    !skl <uid>
  """

  try:
    uid = int(uid)
  except Exception:
    await ctx.channel.send("Invalid UID. The syntax for sharing is:\n\
    `!share_ko_lang <uid>`\
    ")
    return

  try:
    typ, idx, io = tc.get_entry(uid)
  except Exception:
    await ctx.channel.send("Problem not found. Please use a valid UID.")
    return

  await aux.print_tc(ctx, typ, idx, io, ctx.channel.send)

# ========= Prints the available testcases ======= #
@bot.command()
async def tcs_nga(ctx):
  """Shows a list of all stored test case for a certain problem.

  Syntax:
    !tcs_nga <LE/PA/MP><problem #>
    !tn <LE/PA/MP><problem #>
  """

  msg = ctx.message.content
  inp = "".join(msg.split("!tcs_nga ", 1)).split(maxsplit=1)

  is_ok, typ, idx, name = await aux.get_inputs(ctx,inp)

  if not is_ok:
    return

  all_tc = tc.get_all(typ, idx)
  if not all_tc:
    await ctx.channel.send("There are no testcases.")

  output = [(tcs[3], tcs[0]) for tcs in all_tc]

  embed=discord.Embed(
    title="Available Testcases:",
    description="~ for " + str(typ) + str(idx),
    color=0x709bff
  )
  embed.set_author(name="OJ Hacker")

  for cur_tc, cur_output in enumerate(output):
    cur_title = str(cur_tc + 1) + ". UID: " + str(cur_output[0])
    cur_label = "Label: " + str(cur_output[1])
    embed.add_field(name=cur_title, value=cur_label, inline=False)

  await ctx.channel.send(embed=embed)

# ======= ADMIN COMMANDS ====== #
@bot.command()
@commands.check(lambda ctx: getattr(ctx.guild, 'id', None) in cnst.ALLOWED_GUILDS)
@commands.has_any_role(*cnst.ADMIN_ROLES)
async def delete_tc(ctx):
  """Deletes the """

  msg = ctx.message.content
  inp = "".join(msg.split("!delete_tc ", 1)).split(maxsplit=1)

  try:
    uid = int(inp[0])
  except ValueError:
    await ctx.channel.send("The syntax for deletion is:\n\
      `!delete_tc <uid>`\
    ")
    return

  OJ_msg = f"There exists no test case with UID {uid}"
  ok = tc.delete_entry(uid)
  if ok:
    OJ_msg = f"Test case {uid} successfully deleted!"
  else:
    OJ_msg = f"Cannot find test case {uid} :("
  await ctx.channel.send(OJ_msg)

@bot.command()
@commands.check(lambda ctx: getattr(ctx.guild, 'id', None) in cnst.ALLOWED_GUILDS)
@commands.has_any_role(*cnst.ADMIN_ROLES)
async def delete_problem(ctx):
  """UNDER CONSTRUCTION (kapag puno na database)"""
  auth = ctx.message.author
  msg = ctx.message.content
  inp = "".join(msg.split("!delete_problem ", 1)).split(maxsplit=1)

  is_ok, typ, idx, name = await aux.get_inputs(ctx,inp)

  if not is_ok:
    print("NOT OKAY", is_ok, typ, idx, name)
    return

  # warning kasi di pa naman natetest
  await ctx.channel.send("WARNING! THIS FEATURE IS NOT YET TESTED.")

  await ctx.channel.send(f"Are you sure you want to delete {typ}{idx}? (y/n)".upper())
  resp, msg = await aux.wait_response(bot,ctx,auth)

  if resp.lower() == 'y':
    try:
      tc.delete_row(typ, idx)
      await ctx.channel.send(f"Successfully deleted {typ}{idx}.")
    except Exception:
      print(f"{typ}{idx} not found. Cannot be deleted")
  else:
    await msg.add_reaction('👌')
    return

@bot.command()
@commands.check(lambda ctx: getattr(ctx.guild, 'id', None) in cnst.ALLOWED_GUILDS)
@commands.has_any_role(*cnst.ADMIN_ROLES)
async def HARD_RESET(ctx):
  """DELETES EVERYTHING. Use with caution."""

  auth = ctx.message.author
  await ctx.channel.send(cnst.WIPE_MSG.upper())
  resp, msg = await aux.wait_response(bot,ctx,auth)

  if resp.lower() == 'y':
    tc.erase_db()
    await ctx.channel.send(cnst.WIPE_SUCCESS_MSG)
  else:
    await msg.add_reaction('👌')
  return

@bot.command()
@commands.check(lambda ctx: getattr(ctx.guild, 'id', None) in cnst.ALLOWED_GUILDS)
@commands.has_any_role(*cnst.ADMIN_ROLES)
async def PRINT_DB(ctx):
  """Sends all the stored test cases in a problem

  Syntax:
  !PRINT_DB <LE/PA/MP><problem #>
  """

  msg = ctx.message.content
  inp = "".join(msg.split("!PRINT_DB ", 1)).split(maxsplit=1)

  is_ok,typ,idx,name = await aux.get_inputs(ctx,inp)

  if not is_ok:
    print("NOT OKAY", is_ok, typ, idx, name)
    return

  all_tc = tc.get_all(typ, idx)
  if not all_tc:
    await ctx.channel.send("There are no testcases.")
  for tcs in all_tc:
    await aux.print_tc(ctx, typ, idx, tcs, ctx.channel.send)

@bot.command()
@commands.check(lambda ctx: getattr(ctx.guild, 'id', None) in cnst.ALLOWED_GUILDS)
@commands.has_any_role(*cnst.ADMIN_ROLES)
async def PRINT_ALL(ctx):
  """Prints all the stored test cases

  Use with caution as large amount of data might be sent.
  """

  did_printed_smtn = False
  for typ in cnst.VALID_TYPES:
    for idx in range(1, cnst.LEN_TYP[typ]):
      for tcs in tc.get_all(typ, idx):
        did_printed_smtn = True
        await aux.print_tc(ctx, typ, idx, tcs, ctx.channel.send)

  if not did_printed_smtn:
    await ctx.channel.send("There are no test cases in the database")

# ===== Random command here dahil kay Jotan ===== #
@bot.command(pass_context=True)
async def penge_jowa(ctx):
  """For the bored people."""
  import random
  author = ctx.message.author

  await author.create_dm()
  OJ_msg = "Waifu Sent!"
  rt = random.randint(1,len(images.img_lst))
  rd = random.randint(1,1000)
  ct, end = '','.jpg'
  if rd >= 200 and rd < 250:
    rt = random.randint(1,len(images.kanon_lang_malakas))
    embid = discord.Embed(colour=discord.Colour(0xd55f66))
    embid.set_image(url=images.kanon_lang_malakas[rt-1]+end)
    embid.add_field(name="Kanon Kimura uwu", value="*No need to cite. Hmph. STAN ATARASHI GAKKO!*")
    await author.dm_channel.send(embed=embid)
    await ctx.channel.send('STAN ATARASHI GAKKO!')
  elif rd == 171:
    embid = discord.Embed(colour=discord.Colour(0x992d22))
    embid.set_image(url='https://imgur.com/cukHbrY.jpg')
    embid.add_field(name="Selfie Pic Galing sa Phone ng Kaklase Habang nakahiga sa Kama Prongs :o", value="**Congratulations!** You may now request a new idol to be added for the command.\n *The image was given proper consent for it to be used for special purposes*")
    await author.dm_channel.send(embed=embid)
    await ctx.channel.send('CONGRATS!')
  elif rd == 781:
    embid = discord.Embed(colour=discord.Colour(0x992d22))
    embid.set_image(url='https://imgur.com/cqdceQn.jpg')
    embid.add_field(name="Lord God Lord Lord God Miko :o", value="**Congratulations!** You may now request a new idol to be added for the command.\n *The image was given proper consent for it to be used for special purposes*")
    await author.dm_channel.send(embed=embid)
    await ctx.channel.send('CONGRATS!')
  elif rd == 913:
    embid = discord.Embed(colour=discord.Colour(0x992d22))
    embid.set_image(url='https://imgur.com/Tif00Fq.jpg')
    embid.add_field(name="Senpai Gabuuu :o", value="**Congratulations!** You may now request a new idol to be added for the command.\n *The image was given proper consent for it to be used for special purposes*")
    await author.dm_channel.send(embed=embid)
    await ctx.channel.send('CONGRATS!')
  else:
    ct = images.img_lst[rt-1]
    embid = discord.Embed(colour=discord.Colour(0xefae0))
    embid.set_image(url=ct+end)
    embid.add_field(name="Kowean Pop Idol Waifu :>", value="*This image is credited to random Twitter archives the developer downloaded from.\nThe developers are very sorry for the improper citation of the source.*")
    await author.dm_channel.send(embed=embid)
    await ctx.channel.send(OJ_msg)

bot.run(os.getenv('TOKEN'))
