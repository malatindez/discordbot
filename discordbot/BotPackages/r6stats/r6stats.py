import platform
import sys
import os
import discord
import json
import requests
import r6sapi as r6api
SEASON_NUMBER = 16
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
def transformPath(path):
    if platform.system() == "Linux":
        path.replace("\\", "/")    
    return path
import package
from PIL import Image, ImageFont, ImageDraw

def getRank(mmr):
    returnValue = ""
    if mmr <= 800:
        return "unranked.png"
    if(mmr - 1100) <= 500:
        returnValue = "copper" + str(int(5 - (mmr - 1100) // 100))
    elif(mmr - 1600) <= 500:
        returnValue = "bronze" + str(int(5 - (mmr - 1600) // 100))
    elif(mmr - 2100) <= 500:
        returnValue = "silver" + str(int(5 - (mmr - 2100) // 100))
    elif(mmr - 2600) <= 600:
        returnValue = "gold"  + str(int(3 - (mmr - 2600) // 200))
    elif(mmr - 3200) <= 1200:
        returnValue = "platinum" + str(int(3 - (mmr - 2600) // 400))
    elif(mmr - 4400) <= 600:
        returnValue = "diamond"
    elif mmr >= 5000:
        returnValue = "champion"
    return returnValue + ".png"
class Package(package.Package):

    def __init__(self, core):
        self.name = "r6stats"
        super(Package, self).__init__(core)
        self.importance = 255
        x = open("uplay_auth")
        self.auth = r6api.Auth(x.readline().replace("\n", "").replace('\r',''), x.readline().replace("\n", "").replace('\r',''))
    def getCommands(self):
        return [["help", self.help], 
                ["stats", self.stats], ["s", self.stats], 
                ["c", self.connect], ["connect", self.connect ]]
    def getAdditionalGlobalUserValues(self): 
        return [["r6_player_id", "str"]]
    async def help(self, params, message, core):
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "help"),
                             description = self.getText(message.guild.id, message.channel.id, "helpDescription"))
        embed.add_field(name = "stats",
                        value = self.getText(message.guild.id, message.channel.id, "helpStats"),
                        inline = False)
        embed.add_field(name = "connect",
                        value = self.getText(message.guild.id, message.channel.id, "helpConnect"),
                        inline = False)
        await message.channel.send(embed = embed)
    
    async def stats(self, params, message, core):
        id = ""
        
        if len(params) > 0:
            id = params[0].replace("\n", '')
        else:
            try:
                id = self.db.getGlobalUserData(self.name, "r6_player_id", str(message.author.id))
            except:
                pass
        if id == "":
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "statsNDIDB"))
            return
        player = None
        try:
            player = await self.auth.get_player(id, r6api.Platforms.UPLAY)
            await player.load_general()
            await player.load_level()
            await player.check_queues()
        except:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "wrongName"))
            return
        ranks = []
        for i in range(SEASON_NUMBER - 4, SEASON_NUMBER):
            await player.get_rank("emea", i + 1)
        best_mmr = 0
        for i in ranks:
            if i.max_mmr > best_mmr:
                best_mmr = i.max_mmr
        current_rank = transformPath("BotPackages\\r6stats\\ranks\\big\\unranked.png")
        if (ranks[3].wins + ranks[3].losses) >= 10:
            current_rank = transformPath("BotPackages\\r6stats\\ranks\\big\\" + getRank(ranks[3].mmr))
        max_rank = transformPath("BotPackages\\r6stats\\ranks\\small\\" + getRank(best_mmr))
        img_cr = Image.open(current_rank)
        img_mr = Image.open(max_rank)
        img = Image.open(transformPath("BotPackages\\r6stats\\template.png"))
        img.paste(img_cr, (520, 250))
        img.paste(img_mr, (280, 920))
        draw = ImageDraw.Draw(img)
        font32 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 32)
        font48 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 48)
        font56 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 56)
        font64 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 64)
        font72 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 72)
        font80 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 80)
        def drawText(x,y, text, font):
            draw.text((x,y), str(text), (255,255,255), font = font)
        if len(id) <= 8:
            drawText(270,326,id,font80)
        elif len(id) <= 12:
            drawText(270,318,id,font64)
        else:
            drawText(270,310,id,font48)
        
        drawText(1475 - len(id)*13,100,id,font80)
        
        
        if player.level % 10 == player.level:
            drawText(188,316,player.level,font64)   
        elif player.level % 100 == player.level:
            drawText(166,316,player.level,font64)
        else:
            drawText(152,316,player.level,font64)

        drawText(312, 465, player.matches_won,font80)
        drawText(147, 734, player.kills, font80)
        drawText(147, 844, player.matches_won + player.matches_lost, font80)
        drawText(147, 954, int(best_mmr), font80)
        drawText(147, 954, int(best_mmr), font80)
        
        drawText(1220, 288, player.casual.won, font80)
        drawText(1220, 421, player.casual.lost, font80)
        drawText(1906, 986, round(player.ranked.kills / player.ranked.deaths, 2), font80)
        drawText(1220, 689, player.casual.kills, font80)
        drawText(1220, 840, player.casual.deaths, font80)

        drawText(1906, 288, player.ranked.won, font80)
        drawText(1906, 421, player.ranked.lost, font80)
        drawText(1906, 689, player.ranked.kills, font80)
        drawText(1906, 840, player.ranked.deaths, font80)
        
        try:
            drawText(144, 465, round(player.kills / player.deaths, 2), font80)
        except:
            pass
        try:
            drawText(506, 465, str(int(round(player.matches_won / (player.matches_won + player.matches_lost), 2) * 100)) + " %", font80)
        except:
            pass
        try:
            drawText(1906, 552, str(int(round(player.ranked.won / (player.ranked.won + player.ranked.lost), 2) * 100)) + " %", font80)
        except:
            pass
        try:
            drawText(1220, 552, str(int(round(player.casual.won / (player.casual.won + player.casual.lost), 2) * 100)) + " %", font80)
        except:
            pass
        try:
            drawText(1220, 986, round(player.casual.kills / player.casual.deaths, 2), font80)
        except:
            pass

        img.save("tmp.png")
        await message.channel.send(file=discord.File("tmp.png", filename="tmp.png"))
    async def connect(self, params, message, core):
        id = ""
        if len(params) > 0:
            id = params[0].replace("\n", '')
        else:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "noParams"))
            return
        self.db.writeGlobalUserData(self.name, "r6_player_id", message.author.id, str(params[0]))
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectSuccess"))