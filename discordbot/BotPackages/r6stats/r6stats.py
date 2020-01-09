import platform
import sys
import os
import discord
import json
import requests
import r6sapi as r6api

if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
import package
from PIL import Image, ImageFont, ImageDraw
class Package(package.Package):

    def __init__(self, core):
        self.name = "r6stats"
        super(Package, self).__init__(core)
        self.importance = 255
        x = open("uplay_auth")
        self.auth = r6api.Auth(x.readline().replace("\n", "").replace('\r',''), x.readline().replace("\n", "").replace('\r',''))
    def getCommands(self):
        return [["help", self.help], 
                ["stats", self.stats], 
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
            id = params[0]
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
        except:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "wrongName"))
            return
        await player.load_general()
        await player.load_level()
        Rank = await player.get_rank(region="EU")

        img = Image.open("F:\\python\\discordbot2\\discordbot2\\template.png")
        draw = ImageDraw.Draw(img)
        font32 = ImageFont.truetype("F:\\python\\discordbot2\\discordbot2\\BebasNeue-Bold.otf", 32)
        font48 = ImageFont.truetype("F:\\python\\discordbot2\\discordbot2\\BebasNeue-Bold.otf", 48)
        font56 = ImageFont.truetype("F:\\python\\discordbot2\\discordbot2\\BebasNeue-Bold.otf", 56)
        font64 = ImageFont.truetype("F:\\python\\discordbot2\\discordbot2\\BebasNeue-Bold.otf", 64)
        def drawText(x,y, text, font):
            draw.text((x,y), str(text), (255,255,255), font = font)
        drawText(119,250,player.level,font48)
        drawText(240,245,id,font64)
        drawText(110,356,round(float(player.kills)/player.deaths,2),font64)
        drawText(249,356,player.matches_won,font64)
        drawText(398,356,player.matches_won / (player.matches_won + player.matches_lost), font64)
        drawText(138,580,player.kills, font56)
        drawText(138,670,player.matches_won + player.matches_lost, font56)
        drawText(138,750,Rank.max_mmr, font56)
        img.save("tmp.png")
        await message.channel.send(file=discord.File("F:\\python\\discordbot2\\discordbot2\\tmp.png", filename="tmp.png"))
    async def connect(self, params, message, core):
        id = ""
        if len(params) > 0:
            id = params[0]
        else:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "noParams"))
            return
        self.db.writeGlobalUserData(self.name, "r6_player_id", message.author.id, str(params[0]))
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectSuccess"))