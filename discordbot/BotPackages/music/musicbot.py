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
conn = None
async def get_user_id(data, bconn):
    return [client.user.id]
async def guilds_list(data, bconn):
    x = []
    for guild in client.guilds:
        x.append(guild.id)
    return x
voice_clients = []
async def connect(voice_channel_id):
    print(voice_channel_id)
    channel = client.get_channel(voice_channel_id)
    VoiceClient = await channel.connect()
    voice_clients.append([channel, VoiceClient, [None], None, time()])
async def connectCallback(data, bconn):
    t = client.loop.create_task(connect(data[0]))
    while not t.done():
        await asyncio.sleep(0.25)
async def play(voice_channel_id, text_channel_id, filepath, title, formatstr):
    for client in voice_clients:
        if client[0].id == voice_channel_id:
            client[2].append([filepath, title, text_channel_id, formatstr])
async def playCallback(data, bconn):
    client.loop.create_task(play(data[0], data[1], data[2], data[3], data[4]))
async def queuef(vc_id, tc_id, nothingInQueue, queue_for):
    tchannel = client.get_channel(tc_id)
    for VoiceChannel, VoiceClient, queue, ffmpeg in voice_clients:
        if VoiceChannel.id == vc_id:
            embed = None
            print(queue)
            if len(queue) == 1 and queue[0] is None:
                embed = discord.Embed(title=nothingInQueue)
            else:
                embed = discord.Embed(title=queue_for.format(VoiceChannel.name))
                i = 0
                for element in queue[0:10]:
                    embed.add_field(name="№%s" % str(i + 1), value = element[1], inline = False)
                    i += 1
            print(tchannel)
            await tchannel.send(embed=embed)
async def queueCallback(data, bconn):
    client.loop.create_task(queuef(data[0], data[1], data[2], data[3]))
async def queueHandler():
    while True:
        for VoiceChannel, VoiceClient, queue, ffmpeg, timestamp in voice_clients:
            if not VoiceClient.is_connected():
                conn.POST(0, [VoiceChannel.id])
                voice_clients.remove([VoiceChannel, VoiceClient, queue, ffmpeg, timestamp])
                continue
            if VoiceClient.is_playing():
                timestamp = time()
            elif len(queue) > 1:
                print('b)')
                song = queue[1]
                print(song)
                queue.remove(queue[0])
                if len(queue) == 1:
                    queue[0] = None
                ffmpeg = discord.FFmpegPCMAudio(song[0])
                VoiceClient.play(ffmpeg)
                await client.get_channel(song[2]).send(song[3].format(song[1]))
            if time() - timestamp > 120:
                conn.POST(0, [VoiceChannel.id])
                voice_clients.remove([VoiceChannel, VoiceClient, queue, ffmpeg, timestamp])
                continue
            if VoiceChannel.id != VoiceClient.channel.id:
                print(VoiceChannel)
                print(VoiceClient.channel.id)
                try:
                    VoiceClient.move_to(VoiceChannel)
                except:
                    voice_clients.remove(client)
        await asyncio.sleep(1)
    
@client.event
async def on_ready():
    print("Вошёл как " + client.user.name + ". Мой ID: " + str(client.user.id))
    sock.connect(('localhost', 28484))
    global conn
    conn = bconn(sock, callbacks = [[get_user_id, 0], [guilds_list, 1], 
                                    [connectCallback, 0x100], [playCallback, 0x101], [queueCallback, 0x102]])
client.loop.create_task(queueHandler())
client.run(sys.argv[1])
