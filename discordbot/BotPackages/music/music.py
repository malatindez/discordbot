import platform
import sys
import os
import discord
import json
import requests
import re
import random
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
from time import time
import asyncio
import socket
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
            os.system("start python BotPackages\\music\\musicbot.py " + token + "\r\npause")

    def getCommands(self): 
        return [["help", self.help], ["djrole", self.djrole], ["prole", self.prole], 
                ["connectplayer", self.connectPlayer], ["cplayer", self.connectPlayer], 
                ["disconnectplayer", self.disconnectPlayer], ["dplayer", self.disconnectPlayer],
                ["connect", self.connectAndCreatePlayer],
                ["play", self.play], ["p", self.play], 
                ["shuffleq", self.shuffleq],
                ["stop", self.stop], ["status", self.status]]
    
    def getAdditionalGuildValues(self):
        return [["role", "int64"], ["djrole", "int64"], ["playerchannels", "str"]]
    
    def isAbleToUse(self, commandName, member):
        if member.guild_permissions.administrator or member.id == 595328091962867717:
            return True
        if (commandName == 'djrole' or commandName == 'prole' or 
            commandName == "cplayer" or commandName == "connectplayer" or commandName == "status" or
            commandName == "disconnectplayer" or commandName == "dplayer"):
            return False
        if commandName == "play" or commandName == "connect" or commandName == "shuffleq" or commandName == "p":
            x = self.db.getGuildData(self.name, "role", member.guild.id)
            dj = self.db.getGuildData(self.name, "djrole", member.guild.id)
            if x == 0 or dj == 0:
                return True
            MRole = member.guild.get_role(x)
            DJRole = member.guild.get_role(dj)
            for role in member.roles:
                if MRole <= role or DJRole <= role:
                    return True
            return False
        return True
    
    def getUpdateFunctions(self):
        return [self.initNetwork]
    
    async def firstCall(self, message, command):
        if command[0] != "connect":
            await message.delete()

    # update voice channels
    # data == [voice_channel]
    # code - 0
    async def UVC(self, data, conn):
        print('uvc called')
        await self.lock.acquire()
        for g_id in conn.gvc_ids.keys():
            if conn.gvc_ids[g_id] == data[0]:
                try:
                    conn.gvc_ids[g_id] = None
                    conn.player_channel = 0
                    channel = self.core.client.get_guild(g_id).get_channel(connection.player_channel)

                    for role in channel.overwrites.keys():
                        if role.name != '@everyone':
                            self.core.client.loop.create_task(channel.set_permissions(role, overwrite=None))
                except:
                    pass
                break
        self.lock.release()

    async def g_join(self, data, conn):
        await self.lock.acquire()
        conn.guild_ids.append(data[0])
        conn.gvc_ids.update({data[0]: None })
        self.lock.release()

    async def g_remove(self, data, conn):
        await self.lock.acquire()
        conn.guild_ids.remove(data[0])
        del conn.gvc_ids[data[0]]
        self.lock.release()

    async def initNetwork(self, core):
        self.connections = []
        while not hasattr(self, 'network'):
            await asyncio.sleep(1)
        while len(self.connections) != self.botsnum:
            conn, addr = self.network.accept()
            self.connections.append(bconn(conn, callbacks=[[self.UVC, 0], [self.g_join, 1], [self.g_remove, 2]]))
            await asyncio.sleep(0.25)
                
        for connection in self.connections:
            connection.user_id = (await connection.GET(0,[], 0.05))[0]
            connection.guild_ids = await connection.GET(1,[], 0.05)
            connection.gvc_ids = {} # guild and voice channel ids
            connection.player_channel = 0
            for guild_id in connection.guild_ids:
                connection.gvc_ids.update({guild_id: None})
            connection.vc_id = 0

    async def help(self, params, message, core):
        prefix = core.db.getGuildData("Service", "Prefix", message.guild.id)    
        embed = discord.Embed(title = self.getText(message.guild.id, message.channel.id, "help"),
                             description = self.getText(message.guild.id, message.channel.id, "helpDescription"))
        await message.channel.send(embed = embed)
    async def roleStuff(self, params, message, core, v):
        if not ('<@&' in params[0] or '>' in params[0]) and not params[0] == '@everyone':
            await message.channel.send(self.getText(message.guild.id, message.channel.id,"roleError"))
            return
        id = 0
        if not params[0] == '@everyone':
            params[0] = params[0][3:]
            params[0] = params[0][:len(params[0])-1]
            try:
                id = int(params[0])
            except:
                await message.channel.send(self.getText(message.guild.id, message.channel.id,"roleError"))
                return
        self.db.writeGuildData(self.name, v, message.guild.id, id)
    
    async def djrole(self, params, message, core):
        await self.roleStuff(params, message, core, "djrole")

    async def prole(self, params, message, core):
        await self.roleStuff(params, message, core, "role")
        
    async def connectPlayer(self, params, message, core):
        x = json.loads(self.db.getGuildData(self.name, "playerchannels", message.guild.id))
        if message.channel.id not in x:
            x.append(message.channel.id)
            for role in message.channel.overwrites.keys():
                    await message.channel.set_permissions(role, overwrite=None)
            for role in message.guild.roles:
                if role.name=='@everyone':
                    await message.channel.set_permissions(role, overwrite=discord.PermissionOverwrite(
                        create_instant_invite=False,
                        add_reactions=False,
                        read_messages=False,
                        send_messages=False,
                        send_tts_messages=False,
                        manage_messages=False,
                        embed_links=False,
                        read_message_history=False,
                        use_external_emojis=False,
                        mention_everyone=False
                        ))
        else:
            return
        self.db.writeGuildData(self.name, "playerchannels", message.guild.id, json.dumps(x))
        pass

    async def disconnectPlayer(self, params, message, core):
        x = json.loads(self.db.getGuildData(self.name, "playerchannels", message.guild.id))
        try:
            x.remove(message.channel.id)
            for role in message.guild.roles:
                if role.name=='@everyone':
                    await message.channel.set_permissions(role, overwrite=None)
        except:
            pass
        self.db.writeGuildData(self.name, "playerchannels", message.guild.id, json.dumps(x))
        pass

    async def status(self, params, message, core):
        embed = discord.Embed(title=self.getText(message.guild.id, message.channel.id, "statusTitle").format(message.guild.name))
        x = json.loads(self.db.getGuildData(self.name, "playerchannels", message.guild.id))
        itr = 0
        for conn in self.connections:
            if message.guild.id in conn.gvc_ids.keys():
                itr += 1
                vchannel_name = message.guild.get_channel(conn.gvc_ids[message.guild.id])

                if vchannel_name is not None:
                    vchannel_name = vchannel_name.name

                tchannel_name = message.guild.get_channel(conn.player_channel)

                if tchannel_name is not None:
                    tchannel_name = tchannel_name.mention
                if vchannel_name is not None:
                    embed.add_field(
                        name = self.getText(message.guild.id, message.channel.id, "statusName"),
                        value = self.getText(message.guild.id, message.channel.id, "statusValue").format(
                           message.guild.get_member(conn.user_id).mention, vchannel_name, tchannel_name), 
                        inline = False
                        )
                else:
                    
                    embed.add_field(
                        name = self.getText(message.guild.id, message.channel.id, "statusName"),
                        value = self.getText(message.guild.id, message.channel.id, "statusNotPlaying").format(
                           message.guild.get_member(conn.user_id).mention), 
                        inline = False
                        )
            else:
                embed.add_field(
                    name = self.getText(message.guild.id, message.channel.id, "statusBotNotAdded"),
                    value = self.getText(message.guild.id, message.channel.id, "statusURL").format(conn.user_id),
                    inline = False
                    )
        await message.channel.send(embed=embed)
        if len(x) < itr:
            await message.channel.send(
                self.getText(message.guild.id, message.channel.id, "statusNotEnoughPlayers").format(
                str(len(x)), str(itr)))
    async def findUserChannel(self, message):
        if message.author.voice is None:
            return None
        return message.author.voice.channel

    async def findConnection(self, VoiceChannel):
        await self.lock.acquire()
        for c in self.connections:
            for vc_id in c.gvc_ids.values():
                if VoiceChannel.id == vc_id:
                    self.lock.release()
                    return c
        self.lock.release()

    guild_connection_locks = []
    on_message_timestamp = time()
    on_message_pchannels = []
    async def on_message(self, message):
        if self.on_message_pchannels == [] or (time() - self.on_message_timestamp) > 15:
            self.on_message_pchannels = json.loads(self.db.getGuildData(self.name, "playerchannels", message.guild.id))
        self.on_message_timestamp = time()
        if message.channel.id in self.on_message_pchannels:
            #await message.delete()
            pass
    async def connectAndCreatePlayer(self, params, message, core):
        while message.guild.id in self.guild_connection_locks:
            await asyncio.sleep(0.5)
        self.guild_connection_locks.append(message.guild.id)
        VoiceChannel = await self.findUserChannel(message)
        if VoiceChannel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
            self.guild_connection_locks.remove(message.guild.id)
            return
        for c in self.connections:
            if message.guild.id in c.gvc_ids.keys():
                if c.gvc_ids[message.guild.id] == VoiceChannel.id: 
                    await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorAlreadyConnected"))
                    self.guild_connection_locks.remove(message.guild.id)
                    return
        await self.lock.acquire()
        available_players = []
        a = 0
        for player in json.loads(self.db.getGuildData(self.name, "playerchannels", message.guild.id)):
            a = player
            for c in self.connections:
                if a == c.player_channel:
                    a = 0
            if a != 0:
                available_players.append(a)
        if a == 0:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectionErrorNoFreePlayers"))
            self.guild_connection_locks.remove(message.guild.id)
            self.lock.release()
            return
        a = available_players[random.randint(0, len(available_players) - 1)]
        

        tchannel = None
        c = None
        for connection in self.connections:
            flag = False
            for guild_id in connection.gvc_ids.keys():
                if guild_id == VoiceChannel.guild.id:
                    if connection.gvc_ids[guild_id] is not None:
                        break

                    role = None
                    for r in message.guild.get_member(connection.user_id).roles:
                        if r.name != "@everyone":
                            role = r
                    print(role)
                    tchannel = message.guild.get_channel(a)
                    for r in tchannel.overwrites.keys():
                        if r.name != "@everyone":
                            await tchannel.set_permissions(r, overwrite=None)

                    await tchannel.set_permissions(
                        role, overwrite=discord.PermissionOverwrite(
                                    add_reactions=True,
                                    read_messages=True,
                                    send_messages=True,
                                    send_tts_messages=True,
                                    manage_messages=True,
                                    embed_links=True,
                                    read_message_history=True,
                                    use_external_emojis=True,
                                    mention_everyone=True,
                                    manage_permissions=True,
                                    attach_files=True
                                    ))
                    x = self.db.getGuildData(self.name, "role", message.guild.id)
                    dj = self.db.getGuildData(self.name, "djrole", message.guild.id)
                    r = await connection.GET(0x100, [
                        {
                            'VoiceChannelID': VoiceChannel.id, 
                            'TextChannelID': tchannel.id,
                            'prole': x,
                            'djrole': dj
                        },
                        self.localisation.data[self.getChannelLanguage(VoiceChannel.guild.id, tchannel.id)]
                        ], timeout = 30)
                    print(r)

                    if r != ["Success"]: # Error occured
                        for r in tchannel.overwrites.keys():
                            if r.name != '@everyone':
                                self.core.client.loop.create_task(tchannel.set_permissions(r, overwrite=None))
            
                        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectionErrorNoFreeBotsOrPermissions"))
                        self.guild_connection_locks.remove(message.guild.id)
                        self.lock.release()
                        return

                    connection.player_channel = a
                    connection.gvc_ids[guild_id] = VoiceChannel.id
                    flag = True
                    c = connection
            if flag == True:
                break
        self.lock.release()
        self.guild_connection_locks.remove(message.guild.id)

        if tchannel  is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectionErrorNoFreeBotsOrPermissions"))
            return
        
        
        await message.channel.send(self.getText(message.guild.id, message.channel.id, "connectSuccess").format(tchannel.mention))
        return c
    info_extractor = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
    async def doStuff(self, message, errorOutput = True):
        VoiceChannel = await self.findUserChannel(message)
        if VoiceChannel is None:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorChannelNotFound"))
            raise 1
        connection = await self.findConnection(VoiceChannel)
        if connection is None:
            if errorOutput:
                await message.channel.send(self.getText(message.guild.id, message.channel.id, "errorNoBotInChannel"))
                raise 1
            else:
                return VoiceChannel, None
        if message.channel.id != connection.player_channel:
            await message.channel.send(self.getText(message.guild.id, message.channel.id, "warningPlayer").format(
                message.guild.get_channel(connection.player_channel).mention))
        return (VoiceChannel, connection)
   
    async def play(self, params, message, core):
        VoiceChannel, connection = await self.doStuff(message, False)
        if connection is None:
            connection = await self.connectAndCreatePlayer(params, message, core)
        if connection is None:
            return
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
            
        itr = 0
        while hooked_data is None:
            if itr > 60:
                return
            await asyncio.sleep(1)
            itr += 1
        track = 0
        alt_title = 0
        artist = 0
        try:
            track = r['track']
        except:
            pass
        try:
            alt_title = r['alt_title']
        except:
            pass
        try:
            artist = r['artist']
        except:
            pass
        name = message.author.name
        
        if message.author.nick is not None:
            name = message.author.nick 
        connection.POST(0x101, [
            {
                'VoiceChannelID': VoiceChannel.id,
                'TextChannelID': message.channel.id,
                'filepath': hooked_data['filename'],
                'title': r['title'], 
                'track': track,
                'alt_title': alt_title, 
                'artist': artist, 
                'channel': r['uploader'],
                'video_id': r['id'], 
                'duration': r['duration'], 
                'userid': message.author.id,
                'user': name
            }])
    async def shuffleq(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x107, [
            {
                'VoiceChannelID': VoiceChannel.id, 
            }])
    async def stop(self, params, message, core):
        VoiceChannel, connection = await  self.doStuff(message)
        connection.POST(0x108, [
            {
                'VoiceChannelID': VoiceChannel.id, 
                'userid': message.author.id
            }])
    async def on_guild_join(self, guild):
        self.db.writeGuildData(self.name, "playerchannels", guild.id, "[]")
        self.db.writeGuildData(self.name, "role", guild.id, 0)
        self.db.writeGuildData(self.name, "djrole", guild.id, 0)