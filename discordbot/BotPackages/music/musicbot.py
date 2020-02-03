import discord
import sys
import socket
import asyncio
from Request import Request
client = discord.Client()

print(sys.argv[1])



sock = socket.socket()
sock.connect(('localhost', 28484))

# 0 - alive, no response

# 1 - get_user_id
# response:
# User id

# 2 - guilds_list
# response
# guild ids

# 3 - connect
# data[0] - Voice Channel ID

# 4 - play
# data[0] - Voice Channel ID
# data[1] - Text Channel ID
# data[2] - file_path

# 

from time import time
def get_user_id():
    response = bytearray()
    response.extend(int.to_bytes(client.user.id, 8, byteorder='big'))
    return response

def guilds_list():
    response = bytearray()
    response.extend(int.to_bytes(len(client.guilds), 4, byteorder='big'))
    for guild in client.guilds:
        response.extend(int.to_bytes(guild.id, 8, byteorder='big'))
    return response

voice_clients = []
async def connect(voice_channel_id):
    print(voice_channel_id)
    channel = client.get_channel(voice_channel_id)
    VoiceClient = await channel.connect()
    voice_clients.append([channel, VoiceClient, [None], None])

async def play(voice_channel_id, text_channel_id, filepath, title):
    for client in voice_clients:
        if client[0].id == voice_channel_id:
            client[2].append([filepath, title, text_channel_id])
            if client[2][0] == None:
                client[2].remove(client[2][0])
async def queueHandler():
    while True:
        for VoiceChannel, VoiceClient, queue, ffmpeg in voice_clients:
            if not VoiceClient.is_playing():
                if len(queue) > 1:
                    song = queue[1]
                    queue.remove(queue[0])
                    if len(queue) == 1:
                        queue[0] = None

                    ffmpeg = discord.FFmpegPCMAudio(song[0])
                    VoiceClient.play(ffmpeg)
                    await client.get_channel(song[2]).send('Now playing: %s' % song[1])

            if VoiceChannel.id != VoiceClient.channel.id:
                print(VoiceChannel)
                print(VoiceClient.channel.id)
                try:
                    VoiceClient.move_to(VoiceChannel)
                except:
                    voice_clients.remove(client)
        await asyncio.sleep(1)
async def queuef(vc_id, tc_id):
    tchannel = client.get_channel(tc_id)
    for VoiceChannel, VoiceClient, queue, ffmpeg in voice_clients:
        if VoiceChannel.id == vc_id:
            embed = None
            print(queue)
            if queue[0] is None:
                embed = discord.Embed(title='Nothing in queue')
            else:
                embed = discord.Embed(title='Queue for %s' % VoiceChannel.name)
                i = 0
                for element in queue[0:10]:
                    embed.add_field(name="№%s" % str(i + 1), value = element[1], inline = False)
                    i += 1
            print(tchannel)
            await tchannel.send(embed=embed)
ready = False
async def network():
    while not ready:
        print(time())
        await asyncio.sleep(1)
    while True:
        r = Request()
        try:
            r.from_bytes(sock.recv(1024))
        except:
            for i in voice_clients:
                await i[1].disconnect()
            exit()
        if r.code != 0:
            iterator = 0
        if r.code == 1:
            sock.send(Request.create(0,[client.user.id]).to_bytes())
        elif r.code == 2:
            x = []
            for guild in client.guilds:
                x.append(guild.id)
            sock.send(Request.create(0,x).to_bytes())
        elif r.code == 3:
            await connect(r[0])
        elif r.code == 4:
            await play(r[0], r[1], r[2], r[3])
        elif r.code == 5:
            await queuef(r[0], r[1])

        await asyncio.sleep(0.1)

@client.event
async def on_ready():
    global ready
    ready = True
    print("Вошёл как " + client.user.name + ". Мой ID: " + str(client.user.id))

client.loop.create_task(network())
client.loop.create_task(queueHandler())
client.run(sys.argv[1])