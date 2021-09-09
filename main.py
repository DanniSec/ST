#TODO USER NOT FOUND MESSAGE (ERROR HANDLER)
#TODO ADD STATUS
#TODO ADD FOOTER TO EMEBED MESSAGE

from math import ceil
import json
import requests
import discord
from discord.ext import commands, tasks
#from discord.ext.commands import has_permissions
from riotwatcher import LolWatcher, ApiError
import config
import urllib.request
import os
from bs4 import BeautifulSoup
#import re
#from urllib.request import urlopen
from pygicord import Paginator

def get_prefix(bot, message):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if str(message.guild.id) in prefixes:
        return prefixes[str(message.guild.id)]
    return '.'

bot = commands.Bot(command_prefix=get_prefix, help_command=None)


apikey = config.apikey


watcher = LolWatcher(apikey)
token = config.token

imgList = ['img/UNRANKED.png', 'img/IRON.png', 'img/BRONZE.png', 'img/SILVER.png', 'img/GOLD.png', 'img/PLATINUM.png',
           'img/DIAMOND.png', 'img/MASTER.png', 'img/GRANDMASTER.png', 'img/CHALLENGER.png']


@bot.event
async def on_ready():
        print("bot is ready")


def get_pages(ceilLeng, res, loreTitle, champTitle, value):
    pages = []
    for i in range(0, ceilLeng):
        embed = discord.Embed(title=f'{loreTitle}', description=f'**{value.upper()}:** ***{champTitle}***',
                              url=f"https://universe.leagueoflegends.com/en_AU/story/champion/{value.lower()}/",
                              colour=discord.Colour.random())
        embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/11.16.1/img/champion/{value.capitalize()}.png")
        embed.add_field(name="BIOGRAPHY".upper(), value=res[i], inline=True)
        pages.append(embed)
    return(pages)

@bot.command(name='bio')
async def profile(message, value):

    url = f'https://universe.leagueoflegends.com/en_AU/story/champion/{value.lower()}/'
    url2 = f'https://universe.leagueoflegends.com/en_AU/champion/{value.lower()}/'

    res = requests.get(url)
    html_page = res.content

    champAbout = requests.get(url2)
    html_about = champAbout.content
    print(html_about)

    soup = BeautifulSoup(html_page, 'html.parser')
    champContent = soup.find("div", {"id": "Content"})

    soupAbout = BeautifulSoup(html_about, 'html.parser')
    rawChampTitle = soupAbout.find("meta", property="og:description")
    champTitle = rawChampTitle['content']

    title = soup.find("meta", property="og:title")
    desc = soup.find("meta", property="og:description")

    loreTitle = title['content'] if title else "No meta title given"
    rawContent = desc['content'] if desc else "No meta description given"

    if len(rawContent) > 1024:
        leng = len(rawContent)/1024
        x = 1024
        res = [rawContent[y - x:y] for y in range(x, len(rawContent) + x, x)]
        #print(res)
        ceilLeng = ceil(leng)
    else:
        pass

    paginator = Paginator(
        pages=get_pages(ceilLeng, res, loreTitle, champTitle, value),
        timeout=60.0,
    )
    await paginator.start(message)


@bot.command(name='profile')
async def profile(message, *, value):

    rawValue = [x.strip() for x in value.split('-')]
    value = rawValue[0]

    try:
        server = rawValue[1]
    except IndexError:
        server = "eune"


    if server == "eune":
        region = "eun1"
    elif server == "euw":
        region = "euw1"
    elif server == "na":
        region = "na1"
    elif server == "kr":
        region = "kr"

    name_url = watcher.summoner.by_name(region, f'{rawValue[0]}')
    soloRank = watcher.league.by_summoner(region, name_url['id'])
    userPts = rawValue[0] + ".png"
    if (' ' in userPts) == True:
        userPoints = userPts.replace(" ", "")
    else:
        userPoints = userPts

    if (' ' in value) == True:
        opggValue = value.replace(" ", "+")
        opggUrl = f"https://eune.op.gg/summoner/userName={opggValue}"
    else:
        opggUrl = f"https://eune.op.gg/summoner/userName={rawValue[0]}"

    if (' ' in value) == True:
        mpValue = value.replace(" ", "%20")
        urllib.request.urlretrieve(f"https://www.masterypoints.com/image/profile/{mpValue}/{server.lower()}", f"img/{userPoints}")
    else:
        urllib.request.urlretrieve(f"https://www.masterypoints.com/image/profile/{rawValue[0]}/{server.lower()}", f"img/{userPoints}")


    print(soloRank)
    slRank = "UNRANKED"
    fxRank = "UNRANKED"
    for ranks in soloRank:
        temp = ""
        if 'miniSeries' in ranks:
            promoWins = ranks['miniSeries']['wins']
            promoLosses = ranks['miniSeries']['losses']
            temp = f"{ranks['tier']} {ranks['rank']} \nPROMO: {promoWins}W / {promoLosses}L"
        else:
            temp = f"{ranks['tier']} {ranks['rank']} {ranks['leaguePoints']}LP"
        if ranks['queueType'] == "RANKED_SOLO_5x5":
            slRank = temp
        else:
            fxRank = temp
    if slRank != "UNRANKED":
        rank = soloRank[0]['tier']
        rank += '.png'
    else:
        rank = "UNRANKED.png"


    pointsImage = discord.File(f"img/{userPoints}", filename=f"{userPoints}")

    file = discord.File(f"img/{slRank.split()[0]}.png", filename=f"{rank}")
    embed = discord.Embed(colour=discord.Colour.random())

    embed.add_field(name=f"LEVEL", value=f"{name_url['summonerLevel']}")
    embed.add_field(name=f"SOLO RANK",
                        value=f"{slRank}")
    embed.add_field(name=f"FLEX RANK",
                        value=f"{fxRank}")

    embed.set_thumbnail(url=f"attachment://{rank}")


    embed.set_image(url=f"attachment://{userPoints}")

    embed.set_author(name=f"{rawValue[0]} {server.upper()}",
                     url=opggUrl,
                     icon_url=f"http://ddragon.leagueoflegends.com/cdn/11.17.1/img/profileicon/"
                              f"{name_url['profileIconId']}.png")

    await message.channel.send(embed=embed, files=(file, pointsImage))
    os.remove(f"img/{userPoints}")


if config.is_dev:
    print("Running in dev mode!")

bot.run(token)
