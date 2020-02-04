import discord
import sys
import socket
import asyncio
from music_network import bconn
client = discord.Client()

print(sys.argv[1])



sock = socket.socket()

# 0 - get_user_id
# response:
# User id

# 1 - guilds_list
# response
# guild ids

# 2 - connect
# data[0] - Voice Channel ID

# 3 - play
# data[0] - Voice Channel ID
# data[1] - Text Channel ID
# data[2] - file_path
from time import time, sleep
from random import randint
std_delete_after = 60
conn = None
async def get_user_id(data, bconn):
    return [client.user.id]
async def guilds_list(data, bconn):
    x = []
    for guild in client.guilds:
        x.append(guild.id)
    return x
class VClientData:
    def __init__(self, VoiceChannel = None, VoiceClient = None,  queue = [None], ffmpeg = None, timestamp = time()):
        self.VoiceClient = VoiceClient
        self.VoiceChannel = VoiceChannel
        self.queue = queue
        self.ffmpeg = ffmpeg
        self.timestamp = timestamp
        self.repeat = 0
        self.shuffle = 0
    async def update(self):
        print(self.repeat)
        if self.VoiceClient.is_playing():
            self.timestamp = time()
        elif len(self.queue) == 1:
            if self.repeat == 1:
                song = self.queue[0]
                if song is not None:
                    self.ffmpeg = discord.FFmpegPCMAudio(song[0])
                    self.VoiceClient.play(self.ffmpeg)
                    await client.get_channel(song[2]).send(song[3].format(song[1]))
            else:
                self.queue[0] = None
        elif len(self.queue) > 1:
            song = None
            if self.repeat == 0:
                if self.shuffle:
                    rand = randint(1, len(self.queue)-1)
                    song = self.queue[rand]
                    self.queue.remove(self.queue[rand])
                    self.queue.insert(1,song)
                else:
                    song = self.queue[1]
                self.queue.remove(self.queue[0])
            elif self.repeat == 1:
                song = self.queue[0]
            elif self.repeat == 2:
                if self.shuffle:
                    song = self.queue[randint(1, len(self.queue)-1)]
                else:
                    song = self.queue[1]
                buf = self.queue[0]
                self.queue.remove(self.queue[0])
                self.queue.append(buf)
            print(song)
            self.ffmpeg = discord.FFmpegPCMAudio(song[0])
            self.VoiceClient.play(self.ffmpeg)
            await client.get_channel(song[2]).send(song[3].format(song[1]))
            

    async def play(self, data):
        voice_channel_id, text_channel_id, filepath, title, userid, nowplaying, addedToQueue = data
        tchannel = client.get_channel(text_channel_id)
        await tchannel.send(addedToQueue.format(title, tchannel.guild.get_member(userid).mention))
        self.queue.append([filepath, title, text_channel_id, nowplaying, userid])

    async def queuef(self, data):
        vc_id, tc_id, nothingInQueue, queue_for, queue_title = data
        tchannel = client.get_channel(tc_id)
        embed = None
        if len(self.queue) == 1 and self.queue[0] is None:
            embed = discord.Embed(title=nothingInQueue)
        else:
            embed = discord.Embed(title=queue_for.format(self.VoiceChannel.name))
            i = 0
            for element in self.queue[0:10]:
                embed.add_field(name=queue_title.format(str(i + 1), tchannel.guild.get_member(element[4]).name), value = element[1], inline = False)
                i += 1
        print(tchannel)
        await tchannel.send(embed=embed)

    async def pause(self, data):
        vc_id, tc_id, userid, msg = data
        tchannel = client.get_channel(tc_id)
        self.VoiceClient.pause()
        await tchannel.send(msg.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))

    async def resume(self, data):
        vc_id, tc_id, userid, msg = data
        tchannel = client.get_channel(tc_id)
        self.VoiceClient.resume()
        await tchannel.send(msg.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))

    async def skip(self, data):
        vc_id, tc_id, userid, msg, errormsg = data
        tchannel = client.get_channel(tc_id)
        if self.VoiceClient.is_playing():
            self.VoiceClient.stop()
            if self.queue[0] is not None:
                await tchannel.send(msg.format(self.queue[0][1], self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
            else:
                await tchannel.send(msg.format("a song", self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        else:
            await tchannel.send(errormsg)

    async def shufflen(self, data):
        vc_id, tc_id, userid, msg = data
        tchannel = client.get_channel(tc_id)
        self.shuffle = not self.shuffle
        await tchannel.send(msg.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
    
    async def shuffleq(self, data):
        vc_id, tc_id, userid, msg, errormsg = data
        tchannel = client.get_channel(tc_id)
        x = [self.queue[0]]
        self.queue.remove(self.queue[0])
        while len(self.queue) > 0:
            i = randint(0, len(self.queue)-1)
            x.append(self.queue[i])
            self.queue.remove(self.queue[i])
        self.queue.extend(x)
        if len(self.queue) > 1:
            await tchannel.send(msg.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        else:
            await tchannel.send(errormsg)

    async def stop(self, data):
        vc_id, tc_id, userid, msg = data
        tchannel = client.get_channel(tc_id)
        await self.VoiceClient.disconnect()
        await tchannel.send(msg.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))

    async def repeatf(self, data):
        vc_id, tc_id, state, userid, msg, msgQ, msgE, msgD = data
        tchannel = client.get_channel(tc_id)
        if self.repeat == state + 1:
            self.repeat = 0
            await tchannel.send(msgD.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        elif self.queue[0] is not None:  
            self.repeat = state + 1
            if self.repeat == 1:
                await tchannel.send(msg.format(self.queue[0][1], self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
            elif self.repeat == 2:
                await tchannel.send(msgQ.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        else:
            await tchannel.send(msg.format(self.queue[0][1], self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
voice_clients = []
async def connect(voice_channel_id):
    channel = client.get_channel(voice_channel_id)
    VoiceClient = await channel.connect()
    voice_clients.append(VClientData(channel, VoiceClient))
async def connectCallback(data, bconn):
    t = client.loop.create_task(connect(data[0]))
    while not t.done():
        await asyncio.sleep(0.25)

async def generalFunc(func_name, data):
    for vclient in voice_clients:
        if vclient.VoiceChannel.id == data[0]:
            await getattr(vclient, func_name)(data)

async def playCallback(data, bconn):
    client.loop.create_task(generalFunc("play", data))

async def queueCallback(data, bconn):
    client.loop.create_task(generalFunc("queuef", data))

async def pauseCallback(data, bconn):
    client.loop.create_task(generalFunc("pause", data))

async def resumeCallback(data, bconn):
    client.loop.create_task(generalFunc("resume", data))

async def skipCallback(data, bconn):
    client.loop.create_task(generalFunc("skip", data))

async def shufflenCallback(data, bconn):
    client.loop.create_task(generalFunc("shufflen", data))
    
async def shuffleqCallback(data, bconn):
    client.loop.create_task(generalFunc("shuffleq", data))

async def stopCallback(data, bconn):
    client.loop.create_task(generalFunc("stop", data))

async def repeatCallback(data, bconn):
    client.loop.create_task(generalFunc("repeatf", data))


    
async def queueHandler():
    global conn
    while True:
        for vclient in voice_clients:
            if not vclient.VoiceClient.is_connected():
                conn.POST(0, [vclient.VoiceChannel.id])
                voice_clients.remove(vclient)
                continue
            if not vclient.VoiceClient.is_paused():
                await vclient.update()
                if time() - vclient.timestamp > 120:
                    conn.POST(0, [vclient.VoiceChannel.id])
                    voice_clients.remove(vclient)
                    continue
            elif time() - vclient.timestamp > 600:
                conn.POST(0, [vclient.VoiceChannel.id])
                voice_clients.remove(vclient)
                continue
            if vclient.VoiceChannel.id != vclient.VoiceClient.channel.id:
                print(vclient.VoiceChannel)
                print(vclient.VoiceClient.channel.id)
                try:
                    await vclient.VoiceClient.move_to(vclient.VoiceChannel)
                except:
                    voice_clients.remove(vclient)
        await asyncio.sleep(1)
        if conn is not None:
            if conn.dead:
                for vc in voice_clients:
                    await vc.VoiceClient.disconnect()
                print('disconnected')
                conn.loop.stop()
                await asyncio.sleep(2.5)
                
                conn = None
                client.loop.create_task(client.close())
                return
@client.event
async def on_ready():
    print("Вошёл как " + client.user.name + ". Мой ID: " + str(client.user.id))
    sock.connect(('localhost', 28484))
    global conn
    conn = bconn(sock, callbacks = [[get_user_id, 0], [guilds_list, 1], 
                                    [connectCallback, 0x100], [playCallback, 0x101], [queueCallback, 0x102], 
                                    [pauseCallback, 0x103], [resumeCallback, 0x104], [skipCallback, 0x105],
                                    [shufflenCallback, 0x106], [shuffleqCallback, 0x107], [stopCallback, 0x108], 
                                    [repeatCallback, 0x109]])
client.loop.create_task(queueHandler())
client.run(sys.argv[1])
