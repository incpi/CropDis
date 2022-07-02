import times
import time
import scrapetube
import pytube
import re
import json
import nextcord
from cryptography.fernet import Fernet

def vidsearch(q: str, results_type, limit: int = 10):
    lst = []
    videos = scrapetube.get_search(query=q, results_type=results_type, limit=limit)

    if results_type == "video":
        for vid in videos:
            x = vid[results_type + 'Id']
            msg = f"https://www.youtube.com/watch?v={x}"
            yt = pytube.YouTube(msg)
            msg = f"{yt.title}\n{msg}"
            lst.append(msg)

    elif results_type == "channel":
        for vid in videos:
            x = vid[results_type + 'Id']
            msg = "https://www.youtube.com/channel/" + x
            yt = pytube.Channel(msg)
            msg = f"{yt.channel_name}\n{yt.vanity_url}"
            lst.append(msg)

    elif results_type == "playlist":
        for vid in videos:
            x = vid[results_type + 'Id']
            msg = f"https://www.youtube.com/playlist?list={x}"
            yt = pytube.Playlist(msg)
            msg = f"{yt.title} has {yt.length} videos! and {yt.views} views!\n{msg}"
            lst.append(msg)
    print("End_Here", results_type)
    return lst


async def playlist(discord_channel, playlist_link, delay):
    x = re.search("list=.*", playlist_link)
    i = x.group()[5:]
    if i.count("&") != 0:
        x = re.search(".*&", i)
        i = x.group()[:-1]
    videos = scrapetube.get_playlist(i, sleep=delay)
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


def ytctoch(yt):
    try:
        x = scrapetube.get_channel(channel_url=yt)
        for i in x:
            i = i["videoId"]
            i = f"channel/{pytube.YouTube(f'https://www.youtube.com/watch?v={i}').channel_id}"
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


def lister(bot, gid, jsonpath, key):
    data = openfile(jsonpath, key)
    closefile(jsonpath, data, key)
    ls = []
    for i in data['server']:
        if i['gid'] == gid:
            for j in i['gid_p']['yt']:
                g = [bot.get_channel(int(i)).name for i in j['ytc_p']['notifying_discord_channel']]
                msg = "https://www.youtube.com/channel/" + j['ytc']
                yt = pytube.Channel(msg)
                msg = f"{yt.channel_name}\n{yt.vanity_url}" + "  in  >>" + (" ".join(g))
                ls.append(msg)
    return ls


def notify(gid, yt_ch_id, jsonpath, x, key):
    yt_ch_id = re.search("youtube.com.*", yt_ch_id).group()[12:]
    if not yt_ch_id.startswith("c"):
        return 2
    else:
        if yt_ch_id.startswith("c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id.startswith("channel/"):
            yt_ch_id = re.search("channel/.*",
                                 yt_ch_id).group()[8:]
            data = openfile(jsonpath, key)
            for i in data['server']:
                for j in i['gid_p']['yt']:
                    if i["gid"] == gid:
                        if j['ytc'] == yt_ch_id:
                            j['ytc_p']["notify"] = x
                            closefile(jsonpath, data, key)
                            return 0


def ytdict(yt_ch_id, dis_id):
    d2 = {'ytc': yt_ch_id, 'ytc_p': {}}
    d2['ytc_p']["video_id"] = []
    d2['ytc_p']["notify"] = "T"
    d2['ytc_p']["notifying_discord_channel"] = [dis_id]
    return d2


def gdict(guildid, yt_ch_id, dis_id):
    d1 = {'gid': guildid, 'gid_p': {}}
    d1['gid_p']['notify_role'] = 0
    d1['gid_p']['notify_msg'] = 0
    d1['gid_p']['yt'] = []
    d1['gid_p']['yt'].append(ytdict(yt_ch_id, dis_id))
    return d1


def addyttodb(yt_ch_id, dis_id, jsonpath, guildid, key):
    yt_ch_id = re.search("youtube.com.*", yt_ch_id).group()[12:]
    if not yt_ch_id.startswith("c"):
        # "https://www.youtube.com/c/LinusTechTips"
        return 2
    else:
        if yt_ch_id.startswith("c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id == 2:
            return 2
        if yt_ch_id.startswith("channel/"):
            yt_ch_id = re.search("channel/.*", yt_ch_id).group()[8:]
            data = openfile(jsonpath, key)
            lid = "https://www.youtube.com/channel/" + yt_ch_id
            videos = scrapetube.get_channel(channel_url=lid)
            for video in videos:
                x = video['videoId']
                if x is None:
                    return 2
                else:
                    break
            if guildid not in [j['gid'] for j in data['server']]:
                data['server'].append(gdict(guildid, yt_ch_id, dis_id))
            elif yt_ch_id not in [j["ytc"] for i in data['server'] for j in i['gid_p']['yt']]:
                for i in data['server']:
                    i['gid_p']['yt'].append(ytdict(yt_ch_id, dis_id))
            else:
                for i in data['server']:
                    for j in i['gid_p']['yt']:
                        if j['ytc'] == yt_ch_id:
                            j["ytc_p"]['notify'] = "T"
                            if dis_id in j["ytc_p"]['notifying_discord_channel']:
                                return 3
                            else:
                                j["ytc_p"][
                                    'notifying_discord_channel'].append(
                                    dis_id)
            closefile(jsonpath, data, key)
            return 1


def removeyt(guildid, jsonpath, yt_ch_id, key, dis_id):
    yt_ch_id = re.search("youtube.com.*", yt_ch_id).group()[12:]
    if not yt_ch_id.startswith("c"):
        # "https://www.youtube.com/c/LinusTechTips"
        return 2
    else:
        if yt_ch_id.startswith("c/"):
            yt_ch_id = ytctoch(yt_ch_id)
        if yt_ch_id == 2:
            return 2
        if yt_ch_id.startswith("channel/"):
            yt_ch_id = re.search("channel/.*", yt_ch_id).group()[8:]
            data = openfile(jsonpath, key)
            lid = "https://www.youtube.com/channel/" + yt_ch_id
            videos = scrapetube.get_channel(channel_url=lid)
            for video in videos:
                x = video['videoId']
                if x is None:
                    return 2
                else:
                    break
            for i in data['server']:
                if i['gid'] == str(guildid):
                    for j in i['gid_p']['yt']:
                        if j['ytc'] == yt_ch_id:
                            if dis_id in j["ytc_p"]['notifying_discord_channel']:
                                j["ytc_p"]['notifying_discord_channel'].remove(dis_id)
                                return 0
                            else:
                                return 1
                        else:
                            return 2
            closefile(jsonpath, data, key)
            print(data)
            return 1


async def checkallvid(bot, jsonpath, key):
    data = openfile(jsonpath, key)
    print("Now yt channel in corresponding server Checking!")
    for i in data['server']:
        us = [i for i in bot.get_guild(int(i['gid'])).roles if i.name == "Yt_Channel"]
        for j in i['gid_p']['yt']:
            if j['ytc_p']['notify'] == "T":
                dislist = j['ytc_p']['notifying_discord_channel']
                yt_id = j['ytc']
                sleep(1.0)
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


async def creatrroles(interaction, jsonpath, key, name):
    gid = interaction.guild.id
    n = "💚"
    embed = nextcord.Embed(title=name,
                           description=f"for youtube channel notification:....{n[1]}",
                           colour=nextcord.Colour.blue())
    await interaction.send(embed=embed)
    message: nextcord.Message
    async for message in interaction.channel.history():
        if not message.embeds:
            continue
        if message.embeds[0].title == embed.title and message.embeds[0].colour == embed.colour:
            vote = message
            break
    else:
        # something broke
        pass
    data = openfile(jsonpath, key)
    for i in data['server']:
        if i["gid"] == gid:
            i['gid_p']["notify_msg"] = vote.id
    closefile(jsonpath, data, key)
    await vote.add_reaction(n)


def react(bot, payload, path1, k):
    role = None
    n = "💚"
    user = payload.user_id
    gid = payload.guild_id
    meid = payload.message_id
    data = openfile(path1, k)
    closefile(path1, data, k)
    for i in data['server']:
        if i["gid"] == gid:
            g = nextcord.utils.find(lambda l: l.id == gid, bot.guilds)
            if i['gid_p']["notify_msg"] == meid:
                m = nextcord.utils.find(lambda l: l.id == user, g.members)
                if payload.emoji.name == n:
                    role = nextcord.utils.get(g.roles, name="Yt_Channel")
                else:
                    pass
                if role is not None:
                    if m is not None:
                        return [m, role]
                    else:
                        return "user not found"
                else:
                    return "Role not found"
            else:
                return "message id wrong"
        else:
            return "something broke here  />/ reinvite"


def dumpalldata(data, gid, did):
    for i in data['server']:
        if i['gid'] in gid:
            data['server'].remove(i)
        for j in i['gid_p']['yt']:
            templ = []
            for k in j["ytc_p"]['notifying_discord_channel']:
                if k not in did:
                    templ.append(k)
            j["ytc_p"]['notifying_discord_channel'] = templ
            if not j["ytc_p"]['notifying_discord_channel']:
                i['gid_p']['yt'].remove(j)
    return data
