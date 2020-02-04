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
delete_after = 30
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
    async def play(self, data):
        voice_channel_id, text_channel_id, filepath, title, nowplaying, addedToQueue = data
        if self.VoiceClient.is_playing():
            await client.get_channel(text_channel_id).send(addedToQueue.format(title), delete_after = delete_after)
        self.queue.append([filepath, title, text_channel_id, nowplaying])

    async def queuef(self, data):
        vc_id, tc_id, nothingInQueue, queue_for = data
        tchannel = client.get_channel(tc_id)
        embed = None
        if len(self.queue) == 1 and self.queue[0] is None:
            embed = discord.Embed(title=nothingInQueue)
        else:
            embed = discord.Embed(title=queue_for.format(self.VoiceChannel.name))
            i = 0
            for element in self.queue[0:10]:
                embed.add_field(name="№%s" % str(i + 1), value = element[1], inline = False)
                i += 1
        print(tchannel)
        await tchannel.send(embed=embed)

    async def pause(self, data):
        vc_id, tc_id, msg = data
        tchannel = client.get_channel(tc_id)
        self.VoiceClient.pause()
        await tchannel.send(msg.format(self.VoiceChannel.name))

    async def resume(self, data):
        vc_id, tc_id, msg = data
        tchannel = client.get_channel(tc_id)
        self.VoiceClient.resume()
        await tchannel.send(msg.format(self.VoiceChannel.name))

    async def skip(self, data):
        vc_id, tc_id, msg, errormsg = data
        tchannel = self.get_channel(tc_id)
        if self.VoiceClient.is_playing():
            self.VoiceClient.stop()
            if queue[0] is not None:
                await tchannel.send(msg.format(queue[0][1], self.VoiceChannel.name))
            else:
                await tchannel.send(msg.format("a song", self.VoiceChannel.name))
        else:
            await tchannel.send(errormsg)
    
    async def shuffle(self, data):
        tchannel = client.get_channel(tc_id)
        vc_id, tc_id, msg, errormsg = data
        x = [self.queue[0]]
        self.queue.remove(queue[0])
        while len(self.queue) > 0:
            i = randint(0, len(self.queue)-1)
            x.append(self.queue[i])
            self.queue.remove(self.queue[i])
        self.queue.extend(x)
        if len(queue) > 1:
            await tchannel.send(msg.format(self.VoiceChannel.name))
        else:
            await tchannel.send(errormsg)

    async def stop(self, data):
        vc_id, tc_id, msg = data
        tchannel = client.get_channel(tc_id)
        await self.VoiceClient.disconnect()
        await tchannel.send(msg.format(self.VoiceClient.name))

    async def repeat(self, data):
        vc_id, tc_id, msg, msgQ, errormsg = data
        tchannel = client.get_channel(tc_id)
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

async def shuffleCallback(data, bconn):
    client.loop.create_task(generalFunc("shuffle", data))
    
async def stopCallback(data, bconn):
    client.loop.create_task(generalFunc("stop", data))

async def repeatCallback(data, bconn):
    client.loop.create_task(generalFunc("repeat", data))


    
async def queueHandler():
    global conn
    while True:
        for vclient in voice_clients:
            print(vclient.queue)
            if not vclient.VoiceClient.is_connected():
                conn.POST(0, [vclient.VoiceChannel.id])
                voice_clients.remove(vclient)
                continue
            if not vclient.VoiceClient.is_paused():
                if vclient.VoiceClient.is_playing():
                    vclient.timestamp = time()
                elif len(vclient.queue) == 1:
                    vclient.queue[0] = None
                elif len(vclient.queue) > 1:
                    print('b)')
                    song = vclient.queue[1]
                    print(song)
                    vclient.queue.remove(vclient.queue[0])
                    vclient.ffmpeg = discord.FFmpegPCMAudio(song[0])
                    vclient.VoiceClient.play(vclient.ffmpeg)
                    await client.get_channel(song[2]).send(song[3].format(song[1]))
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
                    vclient.VoiceClient.move_to(vclient.VoiceChannel)
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
                                    [shuffleCallback, 0x106], [stopCallback, 0x107], [repeatCallback, 0x108]])
client.loop.create_task(queueHandler())
client.run(sys.argv[1])
