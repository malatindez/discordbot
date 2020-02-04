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
from music_network import bconn
import youtube_dl
outtmpl = 'musicF\\%(id)s'
if platform.system() == "Linux":
    outtmpl = 'music/%(id)s' 
class Package(package.Package):
    def __init__(self, core):
        self.name = "music"
        super(Package, self).__init__(core)
        self.importance = 0
        
        self.lock = asyncio.Lock()

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
        return [["help", self.help], ["play", self.play], ["queue", self.queueF],
                ["pause", self.pause], ["resume", self.resume], ["skip", self.skip],
                ["shuffleq", self.shuffleq], ["shuffle", self.shuffle],["stop", self.stop],
                ["repeat", self.repeat]]
    
    def getUpdateFunctions(self):
        return [self.initNetwork]
    # update voice channels
    # data == [voice_channel]
    # code - 0
    async def UVC(self, data, conn):
        print('uvc called')
        await self.lock.acquire()
        for g_id in conn.gvc_ids.keys():
            if conn.gvc_ids[g_id] == data[0]:
                conn.gvc_ids[g_id] = None
        self.lock.release()
    #item:
    # async def command
    # [command, voiceChannel, additional_data]
    async def initNetwork(self, core):
        self.connections = []
        while not hasattr(self, 'network') or not hasattr(self, 'queue') :
            await asyncio.sleep(1)
        while len(self.connections) != self.botsnum:
            conn, addr = self.network.accept()
            self.connections.append(bconn(conn, callbacks=[[self.UVC, 0]]))
            await asyncio.sleep(0.25)
                
        for connection in self.connections:
            connection.used_id = (await connection.GET(0,[], 0.05))[0]
            connection.guild_ids = await connection.GET(1,[], 0.05)
            connection.gvc_ids = {} # guild and voice channel ids
            for guild_id in connection.guild_ids:
                connection.gvc_ids.update({guild_id: None})
            connection.vc_id = 0

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

    async def findConnection(self, VoiceChannel):
        await self.lock.acquire()
        for c in self.connections:
            for vc_id in c.gvc_ids.values():
                if VoiceChannel.id == vc_id:
                    self.lock.release()
                    return c
        self.lock.release()

    async def connect(self, voice_channel, text_channel):
        await self.lock.acquire()
        for connection in self.connections:
            for guild_id in connection.gvc_ids.keys():
                if guild_id == voice_channel.guild.id:
                    if connection.gvc_ids[guild_id] is not None:
                        break
                    await connection.GET(0x100, [voice_channel.id])
                    connection.gvc_ids[guild_id] = voice_channel.id
                    print(connection.gvc_ids)
                    self.lock.release()
                    return connection
        self.lock.release()

    info_extractor = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
   
    async def play(self, params, message, core):
        VoiceChannel = await self.findUserChannel(message)
        if VoiceChannel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
        hooked_data = None
        def hook(data):
            if not data['status'] == 'downloading':
                print(data)
                nonlocal hooked_data
                hooked_data = data
        
        downloader = youtube_dl.YoutubeDL({'format': 'bestaudio', 'progress_hooks': [hook], 'outtmpl': outtmpl})
        
        url = params[0] # formatting params [Hollywood, Undead, -, Bullet] to "Hollywood Undead - Bullet"
        for i in params[1:]:
            url += " " + i
        
        r = None
        if not isURL(url): # if msg not a url, but a search request: 
            r = self.info_extractor.extract_info("ytsearch:{}".format(url), download=False)
            url = r['entries'][0]['webpage_url']
            r = r['entries'][0]
        else: # if msg is a url:
            r = self.info_extractor.extract_info(url, download=False)
            if 'entries' in r:
                r = r['entries'][0]

        if r['duration'] > 600:
            await text_channel.send(self.getText(message.guild.id, message.channel.id, "errorTooBigDuration"))
            return
        
        try: # checking if song already downloaded
            open(outtmpl % {'id': r['id']},'rb')
            hooked_data = {'filename':str(outtmpl % {'id': r['id']})}
        except FileNotFoundError:
            downloader.download([url])
            
        connection = await self.findConnection(VoiceChannel)

        if connection is None:
            connection = await self.connect(VoiceChannel, message.channel)
        else:
            hooked_data = {'filename':outtmpl % {'id': r['id']}}

        itr = 0
        while hooked_data is None:
            if itr > 60:
                return
            await asyncio.sleep(1)
            itr += 1
        connection.POST(0x101, [VoiceChannel.id, message.channel.id, hooked_data['filename'], r['title'], message.author.id, 
                        self.getText(message.guild.id, message.channel.id, "play"),
                        self.getText(message.guild.id, message.channel.id, "playQueue")])
    async def doStuff(self, message):
        VoiceChannel = await self.findUserChannel(message)
        if VoiceChannel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
            return None
        connection = await self.findConnection(VoiceChannel)
        if connection is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorNoBotInChannel"))
            return None
        return (VoiceChannel, connection)
    async def queueF(self, params, message, core):
        VoiceChannel, connection = await self.doStuff(message)
        connection.POST(0x102, [VoiceChannel.id, message.channel.id, 
                                self.getText(message.guild.id, message.channel.id, "nothingIsPlaying"),
                                self.getText(message.guild.id, message.channel.id, "queueFor"),
                                self.getText(message.guild.id, message.channel.id, "queueTitle")])

    async def pause(self, params, message, core):
        VoiceChannel, connection = await self.doStuff(message)
        connection.POST(0x103, [VoiceChannel.id, message.channel.id, message.author.id, 
                                self.getText(message.guild.id, message.channel.id, "pause")])
    async def resume(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x104, [VoiceChannel.id, message.channel.id, message.author.id, 
                                self.getText(message.guild.id, message.channel.id, "resume")])
    async def skip(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x105, [VoiceChannel.id, message.channel.id, message.author.id,
                                self.getText(message.guild.id, message.channel.id, "skip"),
                                self.getText(message.guild.id, message.channel.id, "skipError")])
    async def shuffle(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x106, [VoiceChannel.id, message.channel.id, message.author.id,
                                self.getText(message.guild.id, message.channel.id, "shuffle")])
    async def shuffleq(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x107, [VoiceChannel.id, message.channel.id, message.author.id,
                                self.getText(message.guild.id, message.channel.id, "shuffleq"),
                                self.getText(message.guild.id, message.channel.id, "shuffleqError")])
    async def stop(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        await self.UVC([VoiceChannel.id], connection)
        connection.POST(0x108, [VoiceChannel.id, message.channel.id, message.author.id,
                                self.getText(message.guild.id, message.channel.id, "stop")]) 
    async def repeat(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        state = 0
        if len(params) != 0:
            if params[0] == "all":
                state = 1
            else:
                await message.channel.send(self.getText(message.guild.id, message.channel.id, "repeatError"))
                return
        connection.POST(0x109, [VoiceChannel.id, message.channel.id,  state, message.author.id,
                                self.getText(message.guild.id, message.channel.id, "repeat"),
                                self.getText(message.guild.id, message.channel.id, "repeatQueue"),
                                self.getText(message.guild.id, message.channel.id, "repeatEnabled"),
                                self.getText(message.guild.id, message.channel.id, "repeatDisabled")]) 