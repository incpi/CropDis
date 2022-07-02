import os
import requests
from nextcord import Interaction
import nextcord
from time import sleep
import times
from nextcord.ext import commands, tasks, application_checks
import datastore as d
import cooldowns
from keep_alive import keep_alive
'''private variable with are needed'''
jsonpath = os.environ["jsonpath"]
key = os.environ['key']
Token = os.environ['tk']
'''loading the variable from encrypt file'''
r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except KeyError:
    print(f"No rate limit")

# bot = commands.Bot(command_prefix="/yt", intents=intents)
# bot = commands.AutoShardedBot(shard_count=5,command_prefix="/yt", intents=intents)
#@cooldowns.cooldown(1, 180, bucket=cooldowns.SlashBucket.channel)

intents = nextcord.Intents.all()
bot = commands.AutoShardedBot(shard_count=1, command_prefix="/yt_", intents=intents)

bot.remove_command("help")


# slash command
#   ping
@bot.slash_command(name="yt_ping", description="Somehow find 'ping-time'")
async def pong(interaction: Interaction):
    x = f'Pong! In {round(bot.latency * 1000)}ms'
    await interaction.send(x)


#   search results
@bot.slash_command(name="yt_search",
                   description="you can search here and get your result")
@application_checks.has_role("Yt_Playlist")
@cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.guild)
async def search_vid(
        interaction: Interaction,

        term_to_find: str = nextcord.SlashOption(
            name="search_for",
            description="enter your term/query to search"),

        ktype: str = nextcord.SlashOption(
            name="typeof",
            description="enter your type of choise to search",
            choices=["video", "channel", "playlist"]),

        limit: int = nextcord.SlashOption(
            name="limit",
            description="how many result you want, range in between 1 to 10(default)",
            default=10)):
    if 1 > limit > 10:
        await interaction.send(
            f"please lower your limit from {limit} to 10 or less",
            ephemeral=True)
    else:
        did = interaction.channel_id
        await interaction.send(f"{term_to_find} search getting ready!!")
        vid = d.vidsearch(term_to_find, ktype, limit)
        x = nextcord.Embed(title=term_to_find + f" with type: {ktype} : top 10 results")
        count = 1
        if not vid:
            await bot.get_channel(int(did)).send("no results!!", ephemeral=True)
        else:
            for i in vid:
                x.add_field(name=count, value=i, inline=False)
                count += 1
            await bot.get_channel(int(did)).send(embed=x)


#   playlist messages
@bot.slash_command(name="yt_playlist",
                   description="send all playlist video in individual message")
@application_checks.has_role("Yt_Playlist")
@cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.guild)
async def all_playlist(interaction: Interaction,

                       playlist_link: str = nextcord.SlashOption(
                           name="playlist_link",
                           description="enter your YouTube full URl of playlist"),

                       discord_channel_id: str = nextcord.SlashOption(
                           name="discord_channel_id",
                           description="enter your discord channel id still if you don't know use /yt_getid.",
                           default="0"),

                       sleep: int = nextcord.SlashOption(
                           name="sleep",
                           description="use sleep between 1(default) and 3 sec and it is gap between 2 messages",

                           default=1)):
    if 3 > sleep > 1:
        us = [i for i in interaction.guild.roles
              if i.mentionable and i.name == "Yt_Channel"]
        if len(us) == 0:
            x = "None"
        else:
            x = us[0].mention
        if discord_channel_id == "0":
            discord_channel_id = interaction.channel_id
        discord_channel = bot.get_channel(int(discord_channel_id))
        chname = discord_channel.name
        mbed = nextcord.Embed(title="Hey!! Playlist request",
                              description=f'''
            Sending you, while grab a coffee!,  
            {x}
            If you are not getting any message in next 2 minutes means
            either you are using personal my mix or any private playlist.
            Please make sure playlist is public "i hope this helps you"
    
            check your channel: > {chname} 
            ''',
                              colour=0x33FFFF)

        await interaction.response.send_message(embed=mbed, ephemeral=True)
        await d.playlist(discord_channel=discord_channel,
                         playlist_link=playlist_link,
                         sleep=sleep)
    else:
        await interaction.response.send_message(f"you entered {sleep} sec and it is more than limit", ephemeral=True)


#   delete messages
@bot.slash_command(name="yt_delete",
                   description="delete last message of define amount")
@application_checks.has_role("Yt_Playlist")
@cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.guild)
async def clear(interaction: Interaction,
                amount: int = nextcord.SlashOption(name="amount",
                                                   description="please enter amount.!! it delete last all message not "
                                                               "restricted to user!!")):
    if amount <= 50:
        channel = interaction.channel
        await channel.purge(limit=amount)
        await interaction.send(f"done!{amount}", ephemeral=True)
    else:
        await interaction.send("please enter value less than 50",
                               ephemeral=True)


#   yt list
@bot.slash_command(name="yt_list", description="it will give you list of youtube notification")
@application_checks.has_role("Yt_Playlist")
async def ytlist(interaction: Interaction):
    gid = interaction.guild_id
    vid = d.lister(bot, gid, jsonpath, key)
    x = nextcord.Embed(title="list of your yt channel in channel")
    count = 1
    for i in vid:
        x.add_field(name=count, value=i, inline=False)
    await interaction.send(embed=x, ephemeral=True)


# start notify
@bot.slash_command(
    name="yt_notifystart",
    description="start notify without adding again for whole server only for previously saved data")
@application_checks.has_role("Yt_Playlist")
async def add_notify(interaction: Interaction,
                     youtube_channel: str = nextcord.SlashOption(
                         name="youtube_channel",
                         description="enter your YouTube full URl of channel",
                         required=True)):
    gid = interaction.guild_id
    x = d.notify(gid, youtube_channel, jsonpath, "T", key)
    if x == 2:
        await interaction.send(
            "no link are present!! or check your link of yt", ephemeral=True)
    elif x == 0:
        await interaction.send("success, link notify start for whole server")


# stop notify
@bot.slash_command(
    name="yt_notifystop",
    description="stop notify without deleting for whole server only for previously saved data")
@application_checks.has_role("Yt_Playlist")
async def stop_notify(interaction: Interaction,
                      youtube_channel: str = nextcord.SlashOption(
                          name="youtube_channel",
                          description="enter your YouTube full URl of channel",
                          required=True)):
    gid = interaction.guild_id
    x = d.notify(gid, youtube_channel, jsonpath, "F", key)
    if x == 2:
        await interaction.send(
            "no link are present!! or check your link of yt", ephemeral=True)
    elif x == 0:
        await interaction.send("success link notify stop for whole server")


#   get discord chl id
@bot.slash_command(name="yt_getid", description="get my discord channel id")
@application_checks.has_role("Yt_Playlist")
@cooldowns.cooldown(1, 300, bucket=cooldowns.SlashBucket.guild)
async def get_id(interaction: Interaction):
    await interaction.send(interaction.channel_id)


#   help
@bot.slash_command(name="yt_help", description="help command for hexatube")
async def cmdhelp(inter: Interaction):
    embed = nextcord.Embed(title="HexaTube Help!!", description="")
    for cmd in bot.get_all_application_commands():
        des = cmd.description
        if not des or des is None or des == "":
            des = "No description"
        embed.add_field(name=f"{cmd.name}", value=des, inline=False)
    await inter.send(embed=embed, ephemeral=True)


# react role
@bot.slash_command(name="yt_roles", description="React below for your roles")
async def create_roles(interaction: Interaction, name: str = nextcord.SlashOption(
    name="title", description="to get notified yt react role message!!"
)):
    await d.creatrroles(interaction, jsonpath, key, name)


# add link to db
@bot.slash_command(name="yt_addlink",
                   description="use this command to initiate process to get notified")
@application_checks.has_role("Yt_Playlist")
async def add(interaction: Interaction,
              youtube_channel: str = nextcord.SlashOption(
                  name="youtube_channel",
                  description="enter your YouTube full URl of channel",
                  required=True),
              discord_channel_id: int = nextcord.SlashOption(
                  name="discord_channel_id",
                  description="enter your discord channel id, if you don't know use /yt_getid command ",
                  default=0)):
    if discord_channel_id == 0:
        discord_channel_id = interaction.channel_id
    gid = str(interaction.guild_id)
    await interaction.send("wait while saving data")
    dis_id = interaction.channel_id
    x = d.addyttodb(youtube_channel, discord_channel_id, jsonpath, gid, key)
    if x == 1:
        await bot.get_channel(dis_id).send("Data saved")
    elif x == 2:
        await bot.get_channel(dis_id).send("check your link of yt")
    elif x == 3:
        await bot.get_channel(dis_id).send("checking and already stored.")
    else:
        await bot.get_channel(dis_id).send("retry after 5 min")


# remove from db
@bot.slash_command(name="yt_removelink",
                   description="use this command to permanently delete your youtube notification data")
@application_checks.has_role("Yt_Playlist")
async def remove(interaction: Interaction,
                 youtube_channel: str = nextcord.SlashOption(
                     name="youtube_channel",
                     description="enter your YouTube full URl of channel",
                     required=True),
                 discord_channel_id: int = nextcord.SlashOption(
                     name="discord_channel_id",
                     description='''
                     enter your discord channel id,still if you don't know use /yt_getid.
                     ''',
                     default=0)):
    if discord_channel_id == 0:
        discord_channel_id = interaction.channel_id
    gid = str(interaction.guild_id)

    x = d.removeyt(gid, jsonpath, youtube_channel, key, discord_channel_id)
    if x == 1:
        await interaction.send(f"{discord_channel_id} - channel id is wrong",
                               ephemeral=True)
    elif x == 2:
        await interaction.send(
            f"{youtube_channel.removeprefix('https://www.youtube.com/')} - Youtube link is wrong",
            ephemeral=True)
    elif x == 3:
        await interaction.send(
            f"{discord_channel_id} is already removed or not set",
            ephemeral=True)
    elif x == 0:
        await interaction.send(
            f"{youtube_channel.removeprefix('https://www.youtube.com/')} " +
            f"from {discord_channel_id} is removed from your Account Data!")


# loop task
@tasks.loop(minutes=5.0)
async def dump_data():
    print(times.now())
    print("checking to dump data from file")
    data = d.openfile(jsonpath, key)
    did = list(
        set([
            k for i in data['server'] for j in i['gid_p']['yt']
            for k in j['ytc_p']["notifying_discord_channel"]
            if (str(bot.get_channel(int(k)))) == "None"
        ]))
    gid = [
        i['gid'] for i in data['server'] if (str(bot.get_guild(i['gid']))) == "None"
    ]
    print(gid, did)
    data = d.dumpalldata(data, gid, did)
    d.closefile(jsonpath, data, key)


@tasks.loop(minutes=5.0)
async def check_videos():
    await d.checkallvid(bot, jsonpath, key)
    print("end_send")


# bot event


# error command
@bot.event
async def on_application_command_error(interaction: Interaction, error):
    error = getattr(error, "original", error)
    if isinstance(error, application_checks.errors.ApplicationMissingRole):
        await interaction.send(f"{error}", ephemeral=True)

    if isinstance(error, cooldowns.CallableOnCooldown):
        await interaction.send(
            f"You are being rate-limited! Retry in `{error.retry_after}` seconds.",
            ephemeral=True)
    else:
        raise error


# on add


@bot.event
async def on_guild_join(guild):
    data = d.openfile(jsonpath, key)
    d1 = {'a_name': guild.name, 'gid': guild.id, 'gid_p': {'notify_msg': 0, "Yt_Channel": 0, 'yt': []}}
    if guild.id not in [i['gid'] for i in data['server']]:
        data['server'].append(d1)
    d.closefile(jsonpath, data, key)
    l=[i.name for i in guild.roles]
    p = l.count("Yt_Playlist")
    c = l.count("Yt_Channel")
    if p < 1:
        await guild.create_role(name="Yt_Playlist")
    if c < 1:
        await guild.create_role(name="Yt_Channel",
                                color=0x78B159,
                                mentionable=True)


# on remove action
@bot.event
async def on_guild_remove(guild):
    print(guild.name)
    data = d.openfile(jsonpath, key)
    for i in data['server']:
        if i['gid'] == str(guild.id):
            data['server'].l̥(i)
    d.closefile(jsonpath, data, key)


@bot.event
async def on_raw_reaction_add(payload):
    msg = d.react(bot, payload, jsonpath, key)
    if isinstance(msg, str):
        await bot.get_channel(payload.channel_id).send(msg)
        sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)
    else:
        await msg[0].add_roles(msg[1])


@bot.event
async def on_raw_reaction_remove(payload):
    msg = d.react(bot, payload, jsonpath, key)
    if isinstance(msg, str):
        await bot.get_channel(payload.channel_id).send(msg)
        sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)
    else:
        await msg[0].remove_roles(msg[1])


@bot.event
async def on_ready():
    print("Bot Now Online!")
    dump_data.start()
    sleep(5.0)
    check_videos.start()


# user login


keep_alive()

try:
    bot.run(Token)
except:
    os.system("kill 1")
    print("kill 1")
