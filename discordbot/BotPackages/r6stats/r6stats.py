import platform
import sys
import os
import discord
import json
import requests
SEASON_NUMBER = 16
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
def transformPath(path):
    if platform.system() == "Linux":
        return path.replace("\\", "/")    
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
        returnValue = "platinum" + str(int(3 - (mmr - 3200) // 400))
    elif(mmr - 4400) <= 600:
        returnValue = "diamond"
    elif mmr >= 5000:
        returnValue = "champion"
    return returnValue + ".png"
class Package(package.Package):

    def __init__(self, core):
        self.name = "r6stats"
        super(Package, self).__init__(core)
        self.img = Image.open(transformPath("BotPackages\\r6stats\\template.png"))
        self.imgb = self.img.copy()

        self.importance = 0
    def getCommands(self):
        return [["help", self.help], 
                ["stats", self.stats], ["s", self.stats], 
                ["c", self.connect], ["connect", self.connect ]]
    def getAdditionalGlobalUserValues(self): 
        return [["r6_player_id", "str"]]
    async def help(self, params, message, core):
        prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)    
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "help"),
                             description = self.getText(message.guild.id, message.channel.id, "helpDescription"))
        embed.add_field(name = "stats",
                        value = self.getText(message.guild.id, message.channel.id, "helpStats").format(prefix),
                        inline = False)
        embed.add_field(name = "connect",
                        value = self.getText(message.guild.id, message.channel.id, "helpConnect").format(prefix),
                        inline = False)
        await message.channel.send(embed = embed)
    
    async def stats(self, params, message, core):
        
        prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)    
        name = ""
        
        if len(params) > 0:
            name = params[0].replace("\n", '')
        else:
            try:
                name = self.db.getGlobalUserData(self.name, "r6_player_id", str(message.author.id))
            except:
                name = message.author.nick[:message.author.nick.find(' ') if message.author.nick.find(' ') != -1 else len(message.author.nick)]
        if name == "":
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "statsNDIDB").format(prefix))
            return
        response = requests.get("https://r6.tracker.network/profile/pc/{0}".format(name))
        userid = None
        try:
            userid =json.loads(requests.get("https://r6tab.com/api/search.php?platform=uplay&search={}".format(name)).content)['results'][0]['p_id']
        except:
            pass
        x = str(response.content)
        if not response.ok:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "wrongName"))
            return
        def findStat(str):
            a = x.find(str)
            end1 = x.find("<", a + len(str) + 1)
            end2 = x.find("\\n", a + len(str) + 1)
            return x[a + len(str): end1 if end1 < end2 else end2]
        best_mmr = int(findStat('Best MMR Rating</div>\\n<div class="trn-defstat__value">\\n').replace(',',''))
        current_rank = transformPath("BotPackages\\r6stats\\ranks\\big\\unranked.png")
        stat = findStat('SHIFTING TIDES</div>\\n<div class="trn-text--dimmed">').replace(',','')
        if stat == 'Unranked':
            best_mmr = 0    
        else:
            s = findStat('<div class="trn-defstat__name">MMR</div>\\n<div class="trn-defstat__value">').replace(',','').replace('\\n','')
            current_rank = transformPath("BotPackages\\r6stats\\ranks\\big\\" + getRank(int(s)))
            
        best_rank = transformPath("BotPackages\\r6stats\\ranks\\small\\" + getRank(best_mmr))
        img_cr = Image.open(current_rank)
        img_mr = Image.open(best_rank)
        
        self.imgb.paste(img_cr, (520, 250))
        self.imgb.paste(img_mr, (280, 920))
        draw = ImageDraw.Draw(self.imgb)
        font32 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 32)
        font48 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 48)
        font56 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 56)
        font64 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 64)
        font72 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 72)
        font80 = ImageFont.truetype(transformPath("BotPackages\\r6stats\\BebasNeue-Bold.otf"), 80)
        def drawText(x,y, text, font):
            draw.text((x,y), str(text), (255,255,255), font = font)
        if len(name) <= 8:
            drawText(270,326,name,font80)
        elif len(name) <= 12:
            drawText(270,318,name,font64)
        else:
            drawText(270,310,name,font48)
        
        drawText(1475 - len(name)*13,100,name,font80)
        
        level = int(findStat('Level</div>\\n<div class="trn-defstat__value">\\n'))
        
        if level % 10 == level:
            drawText(188,316,level,font64)   
        elif level % 100 == level:
            drawText(166,316,level,font64)
        else:
            drawText(152,316,level,font64)



        drawText(312, 465, findStat('PVPMatchesWon">\\n'), font80)
        drawText(147, 734, findStat('PVPKills">\\n'), font80)
        drawText(147, 844, findStat('PVPMatchesPlayed">\\n'), font80)
        drawText(147, 954, int(best_mmr), font80)
        
        drawText(1220, 288, findStat('CasualWins">\\n'), font80)
        drawText(1220, 421, findStat('CasualLosses">\\n'), font80)
        drawText(1220, 689, findStat('CasualKills">\\n'), font80)
        drawText(1220, 840, findStat('CasualDeaths">\\n'), font80)
        drawText(1220, 986, findStat('CasualKDRatio">\\n'), font80)
        drawText(1220, 552, findStat('CasualWLRatio">\\n'), font80)

        drawText(1906, 288, findStat('RankedWins">\\n'), font80)
        drawText(1906, 421, findStat('RankedLosses">\\n'), font80)
        drawText(1906, 689, findStat('RankedKills">\\n'), font80)
        drawText(1906, 840, findStat('RankedDeaths">\\n'), font80)
        drawText(1906, 986, findStat('RankedKDRatio">\\n'), font80)
        drawText(1906, 552,findStat('RankedWLRatio">\\n'), font80)
        
        drawText(144, 465, findStat('PVPKDRatio">\\n'), font80)
        drawText(506, 465, findStat('PVPWLRatio">\\n'), font80)

        self.imgb.save("r6tmp.png")
        await message.channel.send(embed=discord.Embed(title='r6tab.com', url="https://r6tab.com/{}".format(userid)))
        await message.channel.send(file=discord.File("r6tmp.png", filename="r6tmp.png"))
        self.imgb = self.img.copy()
    async def connect(self, params, message, core):
        prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)    
        id = ""
        if len(params) > 0:
            id = params[0].replace("\n", '')
        else:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "noParams").format(prefix))
            return
        self.db.writeGlobalUserData(self.name, "r6_player_id", message.author.id, str(params[0]))
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectSuccess"))