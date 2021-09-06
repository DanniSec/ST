import json
import requests
import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from riotwatcher import LolWatcher, ApiError

def get_prefix(bot, message):
    with open('data/prefixes.json', 'r') as f:
        prefixes = json.load(f)
    if str(message.guild.id) in prefixes:
        return prefixes[str(message.guild.id)]
    return '.'

bot = commands.Bot(command_prefix=get_prefix, help_command=None)

config = open('config.json')
data = json.load(config)
apikey = data['apikey']


watcher = LolWatcher(apikey)
token = data['token']

config.close()

imgList = ['img/IRON.png', 'img/BRONZE.png', 'img/SILVER.png', 'img/GOLD.png', 'img/PLATINUM.png', 'img/DIAMOND.png',
           'img/MASTER.png', 'img/GRANDMASTER.png', 'img/CHALLENGER.png']


@bot.event
async def on_ready():
        print("bot is ready")


@bot.command(name='profile')
async def profile(ctx, message, *, value):

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


    print(f"{region} {server}")

    try:
        name_url = watcher.summoner.by_name(region, f'{rawValue[0]}')
        soloRank = watcher.league.by_summoner(region, name_url['id'])
    except requests.exceptions.HTTPError:
        ("ERROR: SUMMONER NOT FOUND")

    if (' ' in value) == True:
        opggValue = value.replace(" ", "+")
        opggUrl = f"https://eune.op.gg/summoner/userName={opggValue}"
    else:
        opggUrl = f"https://eune.op.gg/summoner/userName={rawValue[0]}"

    if (' ' in value) == True:
        mpValue = value.replace(" ", "%20")
        mpUrl = f"https://www.masterypoints.com/image/profile/{mpValue}/{server.lower()}"
    else:
        mpUrl = f"https://www.masterypoints.com/image/profile/{rawValue[0]}/{server.lower()}"

    rank = soloRank[0]['tier']
    rank += '.png'


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

    file = discord.File(f"img/{slRank.split()[0]}.png", filename=f"{rank}")
    embed = discord.Embed(colour=discord.Colour.random())

    embed.add_field(name=f"LEVEL", value=f"{name_url['summonerLevel']}")
    embed.add_field(name=f"SOLO RANK",
                        value=f"{slRank}")
    embed.add_field(name=f"FLEX RANK",
                        value=f"{fxRank}")

    embed.set_thumbnail(url=f"attachment://{rank}")

    embed.set_image(url=mpUrl)

    embed.set_author(name=f"{rawValue[0]} {server.upper()}",
                     url=opggUrl,
                     icon_url=f"http://ddragon.leagueoflegends.com/cdn/11.17.1/img/profileicon/"
                              f"{name_url['profileIconId']}.png")

    await message.channel.send(embed=embed, file=file)


bot.run(token)