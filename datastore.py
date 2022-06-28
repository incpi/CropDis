import times
import time
import scrapetube
import pytube
import re
import json
import nextcord
from cryptography.fernet import Fernet


def ytctoch(yt):
    try:
        x = scrapetube.get_channel(channel_url=yt)
        for i in x:
            i = i["videoId"]
            i = f"https://www.youtube.com/channel/{pytube.YouTube(f'https://www.youtube.com/watch?v={i}').channel_id}"
            return i
    except:
        return 2


def openfile(jsonpath, key):
    key = key.encode()
    fernet = Fernet(key)
    with open(jsonpath, "r") as d:
        for i in d:
            j = i
            break
    if j.startswith("{"):
        with open(jsonpath, 'rb') as file:
            original = file.read()
        encrypted = fernet.encrypt(original)
        with open(jsonpath, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
    else:
        pass
    with open(jsonpath, 'rb') as enc_file:
        encrypted = enc_file.read()
    decrypted = fernet.decrypt(encrypted)
    with open(jsonpath, 'wb') as dec_file:
        dec_file.write(decrypted)
    with open(jsonpath, "r") as d:
        return json.load(d)


def closefile(jsonpath, data, key):
    key = key.encode()
    with open(jsonpath, "w") as fl:
        json.dump(data, fl, indent=2, sort_keys=True)
    fernet = Fernet(key)
    with open(jsonpath, 'rb') as file:
        original = file.read()
    encrypted = fernet.encrypt(original)
    with open(jsonpath, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)


def ytdict(yt_ch_id, dis_id):
    d2 = {}
    d2['ytc'] = yt_ch_id
    d2['ytc_p'] = {}
    d2['ytc_p']["video_id"] = []
    d2['ytc_p']["notify"] = "T"
    d2['ytc_p']["notifying_discord_channel"] = [dis_id]
    return d2


def gdict(G_Id: str, yt_ch_id, dis_id):
    d1 = {}
    d1['gid'] = G_Id
    d1['gid_p'] = {}
    d1['gid_p']['notify_role'] = 0
    d1['gid_p']['notify_msg'] = 0
    d1['gid_p']['yt'] = []
    d1['gid_p']['yt'].append(ytdict(yt_ch_id, dis_id))
    return d1


def addyttodb(yt_ch_id, dis_id, jsonpath, Gid, key):
    if not yt_ch_id.startswith("https://www.youtube.com/c"):
        # "https://www.youtube.com/c/LinusTechTips"
        return 2
    else:
        if yt_ch_id.startswith("https://www.youtube.com/c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id == 2:
            return 2
        if yt_ch_id.startswith("https://www.youtube.com/channel/"):
            yt_ch_id = re.search("https://www.youtube.com/channel/.*",
                                 yt_ch_id).group()[32:]
            data = openfile(jsonpath, key)
            dis_id = int(dis_id)
            lid = "https://www.youtube.com/channel/" + yt_ch_id
            videos = scrapetube.get_channel(channel_url=lid)
            for video in videos:
                x = video['videoId']
                if x == None:
                    return 2
                else:
                    break
            if Gid not in [j['gid'] for j in data['server']]:
                data['server'].append(gdict(Gid, yt_ch_id, dis_id))
            elif yt_ch_id not in [
                    j["ytc"] for i in data['server'] for j in i['gid_p']['yt']
            ]:
                for i in data['server']:
                    i['gid_p']['yt'].append(ytdict(yt_ch_id, dis_id))
            else:
                for i in data['server']:
                    for j in i['gid_p']['yt']:
                        if j['ytc'] == yt_ch_id:
                            j["ytc_p"]['notify'] = "T"
                            if dis_id in j["ytc_p"][
                                    'notifying_discord_channel']:
                                return 3
                            else:
                                j["ytc_p"]['notifying_discord_channel'].append(
                                    dis_id)
        closefile(jsonpath, data, key)
        return 1


async def checkallvid(bot, jsonpath, key):
    data = openfile(jsonpath, key)
    print("Now yt channel in corresponding server Checking!")
    for i in data['server']:
        us = [
            i for i in bot.get_guild(int(i['gid'])).roles
            if i.mentionable and i.name == "Yt_Channel"
        ]
        for j in i['gid_p']['yt']:
            if j['ytc_p']['notify'] == "T":
                dislist = j['ytc_p']['notifying_discord_channel']
                yt_id = j['ytc']
                time.sleep(1.0)
                kl = 0
                te, cdc = [], []
                lst = j['ytc_p']['video_id']
                lid = "https://www.youtube.com/channel/" + yt_id
                videos = scrapetube.get_channel(channel_url=lid)
                for video in videos:
                    if kl < 10:
                        x = video['videoId']
                        if x in lst:
                            try:
                                cdc.append(lst.index(x))
                            except IndexError:
                                cdc.append(9)
                            except:
                                pass
                        te.append(x)
                        if x not in lst:
                            for discord_channel_id in dislist:
                                h = bot.get_channel(int(discord_channel_id))
                                msg = f"https://www.youtube.com/watch?v={x}"
                                yt = pytube.YouTube(msg)
                                if len(us) != 0:
                                    msg = f"Hey!! {us[0].mention} \n>> __**{yt.author}**__ has uploaded *{msg}*"
                                else:
                                    msg = f"Hey!! __**{yt.author}**__ has uploaded {msg}"
                                await h.send(str(f"{msg}"))
                                print(msg)
                        kl += 1
                    else:
                        break  # 10 done
                j['ytc_p']['video_id'] = te
            else:
                pass  # notify F
        print(times.now())
        closefile(jsonpath, data, key)


async def playlist(discord_channel, playlist_link, sleep):
    x = re.search("list=.*", playlist_link)
    i = x.group()[5:]
    if i.count("&") != 0:
        x = re.search(".*&", i)
        i = x.group()[:-1]
    videos = scrapetube.get_playlist(i, sleep=sleep)
    kl = 1
    for video in videos:
        x = video['videoId']
        msg = f"https://www.youtube.com/watch?v={x}"
        yt = pytube.YouTube(msg)
        msg = f"Hey!! {yt.author} has uploaded {msg} {yt.title} on{yt.publish_date} video"
        await discord_channel.send(str(msg))
        kl += 1
    await discord_channel.send(f"playlist is completed all the {kl} videos")
    print("end_playlist")


def vidsearch(q, type, limit=10):
    lst = []
    type = int(type)
    ls = {1: "video", 2: "channel", 3: "playlist"}
    strt = str(ls[type])
    videos = scrapetube.get_search(query=q, results_type=strt, limit=limit)

    if type == 1:
        for vid in videos:
            x = vid[strt + 'Id']
            msg = f"https://www.youtube.com/watch?v={x}"
            yt = pytube.YouTube(msg)
            msg = f"{yt.title}\n{msg}"
            lst.append(msg)

    elif type == 2:
        for vid in videos:
            x = vid[strt + 'Id']
            msg = "https://www.youtube.com/channel/" + x
            yt = pytube.Channel(msg)
            msg = f"{yt.channel_name}\n{yt.vanity_url}"
            lst.append(msg)

    elif type == 3:
        for vid in videos:
            x = vid[strt + 'Id']
            msg = f"https://www.youtube.com/playlist?list={x}"
            yt = pytube.Playlist(msg)
            msg = f"{yt.title} has {yt.length} videos! and {yt.views} views!\n{msg}"
            lst.append(msg)
    print("End_Here")
    return lst


vidsearch("anime", "1")


async def creatrroles(interaction, jsonpath, key, name):
    gid = interaction.guild.id
    n = ["💙", "💚"]
    embed = nextcord.Embed(title=name,
                           description=f'''
                           for sending the youtube playlist:....{n[0]}\n
                           for youtube channel notification:....{n[1]}"
            ''',
                           colour=nextcord.Colour.blue())
    await interaction.send(embed=embed)
    message: nextcord.Message
    async for message in interaction.channel.history():
        if not message.embeds:
            continue
        if message.embeds[0].title == embed.title and message.embeds[
                0].colour == embed.colour:
            vote = message
            break
    else:
        # something broke
        pass
    data = openfile(jsonpath, key)
    for i in data['server']:
        if i["gid"] == str(gid):
            i['gid_p']["notify_msg"] = vote.id
            i['gid_p']["role_id"] = [
                i.id for i in interaction.guild.roles if i.name == "Yt_Channel"
            ]
    closefile(jsonpath, data, key)
    await vote.add_reaction(n[0])
    await vote.add_reaction(n[1])


def react(bot, payload, path1, k):
    role = None
    n = ["💙", "💚"]
    user = payload.user_id
    gid = payload.guild_id
    meid = payload.message_id
    data = openfile(path1, k)
    closefile(path1, data, k)
    for i in data['server']:
        if i["gid"] == str(gid):
            g = nextcord.utils.find(lambda g: g.id == gid, bot.guilds)
            if i['gid_p']["notify_msg"] == meid:
                m = nextcord.utils.find(lambda m: m.id == user, g.members)
                if payload.emoji.name == n[0]:
                    role = nextcord.utils.get(g.roles, name="Yt_Playlist")
                elif payload.emoji.name == n[1]:
                    role = nextcord.utils.get(g.roles, name="Yt_Channel")
                else:
                    pass
                if role is not None:
                    if m is not None:
                        return [m, role]
                    else:
                        return ("user not found")
                else:
                    return ("Role not found")
            else:
                return ("message id wrong")


def notify(gid, yt_ch_id, jsonpath, x, key):
    if not yt_ch_id.startswith("https://www.youtube.com/c"):
        return 2
    else:
        if yt_ch_id.startswith("https://www.youtube.com/c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id.startswith("https://www.youtube.com/channel/"):
            yt_ch_id = re.search("https://www.youtube.com/channel/.*",
                                 yt_ch_id).group()[32:]
            data = openfile(jsonpath, key)
            for i in data['server']:
                for j in i['gid_p']['yt']:
                    if i["gid"] == str(gid):
                        if j['ytc'] == yt_ch_id:
                            j['ytc_p']["notify"] = x
                            closefile(jsonpath, data, key)
                            return 0


def removeyt(Gid, jsonpath, yt_ch_id, key, dis_id=0):
    if not yt_ch_id.startswith("https://www.youtube.com/c"):
        # "https://www.youtube.com/c/LinusTechTips"
        return 2
    else:
        if yt_ch_id.startswith("https://www.youtube.com/c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id == 2:
            return 2
        if yt_ch_id.startswith("https://www.youtube.com/channel/"):
            yt_ch_id = re.search("https://www.youtube.com/channel/.*",
                                 yt_ch_id).group()[32:]
            data = openfile(jsonpath, key)
            dis_id = int(dis_id)
            lid = "https://www.youtube.com/channel/" + yt_ch_id
            videos = scrapetube.get_channel(channel_url=lid)
            for video in videos:
                x = video['videoId']
                if x == None:
                    return 2
                else:
                    break
            for i in data['server']:
                if i['gid'] == str(Gid):
                    for j in i['gid_p']['yt']:
                        if j['ytc'] == yt_ch_id:
                            if dis_id in j["ytc_p"][
                                    'notifying_discord_channel']:
                                j["ytc_p"]['notifying_discord_channel'].remove(
                                    dis_id)
                                return 0
                            else:
                                return 1
                        else:
                            return 2
            closefile(jsonpath, data, key)
            print(data)
            return 1


def dumpalldata(data, did):
    for i in data['server']:
        for j in i['gid_p']['yt']:
            l = []
            for k in j["ytc_p"]['notifying_discord_channel']:
                if k not in did:
                    l.append(k)
            j["ytc_p"]['notifying_discord_channel'] = l
            if j["ytc_p"]['notifying_discord_channel'] == []:
                i['gid_p']['yt'].remove(j)
        return data
