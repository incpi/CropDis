import os
import requests
from nextcord import Interaction
import nextcord
import time
import times
from nextcord.ext import commands, tasks
import datastore as d
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
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="/yt", intents=intents)


@tasks.loop(minutes=5.0)
async def check_videos():
    await d.checkallvid(bot, jsonpath, key)
    print("end_send")


@bot.slash_command(name="yt_addlink",
                   description="add link to save data in system")
async def add(interaction: Interaction,
              youtube_channel: str,
              discord_channel_id=0):
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


@bot.slash_command(name="yt_getid", description="get my dicordid")
async def test_links(interaction: Interaction):
    await interaction.send(interaction.channel_id)


@bot.slash_command(name="yt_removelink",
                   description="remove yt link to save data in system")
async def remove(interaction: Interaction,
                 youtube_channel: str,
                 discord_channel_id="0"):
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


@bot.slash_command(
    name="yt_notifystart",
    description=
    "link-notify -start for whole server only for previously saved data")
async def add_notify(interaction: Interaction, youtube_channel: str):
    gid = str(interaction.guild_id)
    x = d.notify(gid, youtube_channel, jsonpath, "T", key)
    if x == 2:
        await interaction.send(
            "no link are present!! or check your link of yt", ephemeral=True)
    elif x == 0:
        await interaction.send("success link notify start for whole server")


@bot.slash_command(
    name="yt_notifystop",
    description=
    "link-notify -stop for whole server only for previously saved data")
async def stop_notify(interaction: Interaction, youtube_channel: str):
    gid = str(interaction.guild_id)
    x = d.notify(gid, youtube_channel, jsonpath, "F", key)
    if x == 2:
        await interaction.send(
            "no link are present!! or check your link of yt", ephemeral=True)
    elif x == 0:
        await interaction.send("success link notify stop for whole server")


@commands.has_role("Yt_Playlist")
@bot.slash_command(name="yt_playlist")
async def all_playlist(interaction: Interaction,
                       playlist_link: str,
                       discord_channel_id=0,
                       sleep=1):
    us = [
        i for i in interaction.guild.roles
        if i.mentionable and i.name == "Yt_Channel"
    ]
    if len(us) == 0:
        x = "None"
    else:
        x = us[0].mention
    if discord_channel_id == 0:
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


@commands.has_role("Yt_Playlist")
@bot.slash_command(name="yt_search",
                   description="search video>1,channel>2,playlist>3")
async def search_vid(interaction: Interaction,
                     term_to_find,
                     type="1",
                     limit=10):
    did = interaction.channel_id
    await interaction.send(f"{term_to_find} search getting ready!!")
    vid = d.vidsearch(term_to_find, type, limit)
    x = nextcord.Embed(title=term_to_find + f" with type: {type}" +
                       " : top 10 results")
    count = 1
    for i in vid:
        x.add_field(name=count, value=i, inline=False)
        count += 1
    await bot.get_channel(int(did)).send(embed=x)


@bot.slash_command(name="yt_ping", description="Somehow find 'ping-time'")
async def pong(interaction: Interaction):
    x = f'Pong! In {round(bot.latency * 1000)}ms'
    await interaction.send(x)


@bot.slash_command(name="yt_delete",
                   description="delete last message of define amount")
async def clear(interaction: Interaction, amount: int):
    if amount <= 500:
        channel = interaction.channel
        await channel.purge(limit=amount)
        await interaction.send(f"done!{amount}", ephemeral=True)
    else:
        await interaction.send("please enter value less than 500",
                               ephemeral=True)


@bot.slash_command(name="yt_roles")
async def create_roles(interaction: Interaction,
                       name="Read below for your roles"):
    await d.creatrroles(interaction, jsonpath, key, name)


@bot.event
async def on_raw_reaction_add(payload):
    msg = d.react(bot, payload, jsonpath, key)
    if type(msg) == type("1"):
        await bot.get_channel(payload.channel_id).send(msg)
        time.sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)
    else:
        await msg[0].add_roles(msg[1])
        await bot.get_channel(payload.channel_id
                              ).send(f"{msg[0].name} add {msg[1].name}")
        time.sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)


@bot.event
async def on_raw_reaction_remove(payload):
    msg = d.react(bot, payload, jsonpath, key)
    if type(msg) == type("1"):
        await bot.get_channel(payload.channel_id).send(msg)
        time.sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)
    else:
        await msg[0].remove_roles(msg[1])
        await bot.get_channel(payload.channel_id
                              ).send(f"{msg[0].name} remove {msg[1].name}")
        time.sleep(1.0)
        await bot.get_channel(payload.channel_id).purge(limit=1)


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
    print(did)
    data = d.dumpalldata(data, did)
    d.closefile(jsonpath, data, key)


@bot.slash_command(name="yt_delete_roles",
                   description="it will delete only roles created by me.")
async def delete_roles(interaction: Interaction):
    ls = [
        i for i in interaction.guild.roles
        if i.name in ["Yt_Channel", "Yt_Playlist"]
    ]
    for i in ls:
        await nextcord.Role.delete(i)
    await interaction.send(f"delete_role {' '.join(ls)}")


@bot.event
async def on_guild_join(guild):
    print(guild.name)

    data = d.openfile(jsonpath, key)
    d1 = {
        'gid': str(guild.id),
        'gid_p': {
            'notify_role': 0,
            'notify_msg': 0,
            'yt': []
        }
    }
    print(d1)
    if guild.id not in [i['gid'] for i in data['server']]:
        data['server'].append(d1)
    d.closefile(jsonpath, data, key)
    listofrole = [print(i.name) for i in guild.roles]
    if "Yt_Playlist" not in listofrole:
        await guild.create_role(name="Yt_Playlist")
    if "Yt_Channel" not in listofrole:
        await guild.create_role(name="Yt_Channel",
                                color=0x78B159,
                                mentionable=True)
    member = [
        i.user
        async for i in guild.audit_logs(action=nextcord.AuditLogAction.bot_add,
                                        limit=1)
    ][0]
    await member.add_roles(nextcord.utils.get(guild.roles, name="Yt_Playlist"))
    await member.add_roles(nextcord.utils.get(guild.roles, name="Yt_Channel"))


@bot.event
async def on_guild_remove(guild):
    print(guild.name)
    data = d.openfile(jsonpath, key)
    for i in data['server']:
        if i['gid'] == str(guild.id):
            data['server'].remove(i)
    d.closefile(jsonpath, data, key)


@bot.event
async def on_ready():
    print("Bot Now Online!")
    dump_data.start()
    check_videos.start()


keep_alive()

try:
    bot.run(Token)
except:
    os.system("kill 1")
    print("kill 1")