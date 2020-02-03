import platform
import sys
import os
import discord
import json
import requests
import re
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))' #domain...
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
def isURL(url):
    return re.match(regex, url) is not None
if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/..")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\..")
import package
from PIL import Image, ImageFont, ImageDraw
import subprocess
import socket
import asyncio
from queue import Queue
from Request import Request
import youtube_dl
outtmpl = 'music\\%(id)s'
if platform.system() == "Linux":
    outtmpl = 'music/%(id)s' 
class Package(package.Package):
    def __init__(self, core):
        self.name = "music"
        super(Package, self).__init__(core)
        self.importance = 0
        
        self.network = socket.socket()
        self.network.bind(('localhost', 28484))
        self.network.listen(16)

        self.musicbots = []
        open('musictokens', 'a').close()
        lines = open('musictokens', 'r').readlines()
        self.botsnum = len(lines)
        for token in lines:
            token = token.replace('\r', '').replace('\n', '')
            os.system("start python BotPackages\\music\\musicbot.py " + token)
        self.queue = Queue()
    def getCommands(self): 
        return [["help", self.help], ["play", self.play], ["queue", self.queueF]]
    
    def getUpdateFunctions(self):
        return [self.musicNetwork]
    #item:
    # async def command
    # [command, voiceChannel, additional_data]
    async def musicNetwork(self, core):
        alive = Request.create(0, []).to_bytes()
        response = Request()
        def intToByte(x):
            return int.to_bytes(x,1,byteorder='big')

        connections = []
        while not hasattr(self, 'network') or not hasattr(self, 'queue') :
            await asyncio.sleep(1)
        while len(connections) != self.botsnum:
            conn, addr = self.network.accept()
            connections.append([conn, addr])
            await asyncio.sleep(0.25)
        await asyncio.sleep(10)
        
        for connection in connections:
            connection[0].send(Request.create(1,[]).to_bytes())
        await asyncio.sleep(1)
        # loading user id
        for connection in connections:
            response.from_bytes(connection[0].recv(1024))
            connection.append(response[0])

        for connection in connections:
            connection[0].send(Request.create(2,[]).to_bytes())
        await asyncio.sleep(1)
        # loading guilds
        for connection in connections:
            response.from_bytes(connection[0].recv(1024))
            connection.append(response.data)
            connection.append([]) # list of guilds and voice chats where bot is playing
        print(connections)

        while True:
            if self.queue.empty():
                for connection in connections:
                    connection[0].send(alive)
                await asyncio.sleep(1)
            else:
                item = self.queue.get()
                self.core.client.loop.create_task(item[0](item[1], item[2], connections, item[3:]))

    async def help(self, params, message, core):
        prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)    
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "help"),
                             description = self.getText(message.guild.id, message.channel.id, "helpDescription"))
        await message.channel.send(embed = embed)


    async def findUserChannel(self, message):
        for voice_channel in message.guild.voice_channels:
            for member in voice_channel.members:
                if member == message.author:
                    return voice_channel
        return None

    def connect(self, voice_channel, text_channel, connections):
        for connection in connections:
            if voice_channel.guild.id in connection[3]:
                flag = False
                for guild_id, vc_id in connection[4]:
                    if guild_id == voice_channel.guild.id:
                        flag = True
                        break
                if not flag:
                    connection[0].send(Request.create(3, [voice_channel.id]).to_bytes())
                    connection[4].append([voice_channel.guild.id, voice_channel.id])
                    return connection
    info_extractor = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    async def playC(self, voice_channel, text_channel, connections, data):
        hooked_data = None
        def hook(data):
            if not data['status'] == 'downloading':
                print(data)
                nonlocal hooked_data
                hooked_data = data
        downloader = youtube_dl.YoutubeDL({'format': 'worstaudio', 'progress_hooks': [hook], 'outtmpl': outtmpl})
        url = data[0][0]
        for i in data[0][1:]:
            url += " " + i
        r = None
        if not isURL(url):
            r = self.info_extractor.extract_info("ytsearch:{}".format(url), download=False)
            url = r['entries'][0]['webpage_url']
            r = r['entries'][0]
        else:
            r = self.info_extractor.extract_info(url, download=False)
            if 'entries' in r:
                r = r['entries'][0]

        if r['duration'] > 600:
            await text_channel.send(self.getText(text_channel.guild.id, text_channel.id, "errorTooBigDuration"))
            return
        try:
            open(outtmpl % {'id': r['id']},'rb')
            hooked_data = {'filename':str(outtmpl % {'id': r['id']})}
        except FileNotFoundError:
            downloader.download([url])

        connection = None

        for c in connections:
            for guild_id, vc_id in c[4]:
                if voice_channel.id == vc_id:
                    connection = c
                    hooked_data = {'filename':outtmpl % {'id': r['id']}}
        if connection == None:
            connection = self.connect(voice_channel, text_channel, connections)
        while hooked_data is None:
            await asyncio.sleep(1)
        print(hooked_data)
        connection[0].send(Request.create(4, [voice_channel.id, text_channel.id, hooked_data['filename'], r['title']]).to_bytes())
    async def play(self, params, message, core):
        channel = await self.findUserChannel(message)
        if channel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
        self.queue.put([self.playC, channel, message.channel, params[0:]])


    async def queueC(self, voice_channel, text_channel, connections, data):
        connection = None
        for c in connections:
            for guild_id, vc_id in c[4]:
                if voice_channel.id == vc_id:
                    connection = c
        if connection is None:
            await text_channel.send(self.getText(texxt_channel.guild.id, text_channel.id, "errorNoBotInChannel"))
            return
        connection[0].send(Request.create(5, [voice_channel.id, text_channel.id]).to_bytes())
    async def queueF(self, params, message, core):
        channel = await self.findUserChannel(message)
        if channel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
        self.queue.put([self.queueC, channel, message.channel, params[0:]])