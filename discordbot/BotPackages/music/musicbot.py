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
from music_queue import Song, SongQueue
class VClientData:
    def __init__(self, VoiceChannel = None, VoiceClient = None, TextChannel = None, disconnectMSG = None,
                disconnectMSG2 = None, enqueuedby = None, queue = [None], role = None):
        self.VoiceClient = VoiceClient
        print(VoiceClient)
        self.VoiceChannel = VoiceChannel
        self.TextChannel = TextChannel
        self.disconnectMSG = disconnectMSG
        self.disconnectMSG2 = disconnectMSG2
        self.queue = SongQueue(enqueuedby)
        print(queue)
        print(self.queue)
        self.role = role
        self.timestamp = time()
        self.timestampm = time()
        self.Text = "Status:"
        self.msg = None
    async def delete(self):
        try:
            await self.VoiceClient.disconnect()
        except Exception as e:
            print(e)
        try:
            await self.role.delete()
        except Exception as e:
            print(e)
    def __del__(self):
        t = client.loop.create_task(self.delete())
        sleep(3)

    async def on_reaction_add(self, reaction, user):
        if not user.id == client.user.id:
            if str(reaction.emoji) == '⏯️':
                if self.queue.paused:
                    self.VoiceClient.resume()
                else:
                    self.VoiceClient.pause()
                self.queue.paused = not self.queue.paused
            elif str(reaction.emoji) == '⏭️':
                self.VoiceClient.stop()
            elif str(reaction.emoji) == '🔀':
                self.queue.shuffle = not self.queue.shuffle
            elif str(reaction.emoji) == '🔁':
                if self.queue.repeat == 2:
                    self.queue.repeat = -1
                self.queue.repeat = self.queue.repeat + 1
            elif str(reaction.emoji) == '⬅️':
                if self.queue.page == 0:
                    self.queue.page = int((len(self.queue.queue) - 2) / 7)
                else:
                    self.queue.page = self.queue.page - 1
            elif str(reaction.emoji) == '➡️':
                if len(self.queue.queue) > self.queue.page * 7 + 8:
                    self.queue.page = self.queue.page + 1
                else:
                    self.queue.page = 0
            await reaction.remove(user)
            print(self.queue.page)
    async def inactivityMSG(self):
        await self.TextChannel.send(self.disconnectMSG.format(self.VoiceChannel.name))

    async def nooneMSG(self):
        await self.TextChannel.send(self.disconnectMSG2.format(self.VoiceChannel.name))


    

    def __str__(self):
        a = ("VoiceChannel: " + str(self.VoiceChannel))
        a += ("\nVoiceClient: " + str(self.VoiceClient))
        a += ("\nTextChannel: " + str(self.TextChannel))
        a += ("\nshuffle: " + str(self.shuffle))
        a += ("\nrepeat: " + str(self.repeat))
        a += ("\nQueue: " + str(self.queue))
        return a

    async def update(self):
        try:
            if len(self.VoiceChannel.members) > 1:
                self.timestampm = time()
            if self.VoiceClient.is_playing():
                self.timestamp = time()
            elif not self.VoiceClient.is_paused():
                song = self.queue.next()
                if song is not None:
                    self.ffmpeg = discord.FFmpegPCMAudio(song.filepath)
                    self.VoiceClient.play(self.ffmpeg)
                    await client.get_channel(song.TextChannelID).send(song.play.format(song.title))
            if len(self.queue.queue) < self.queue.page * 7 + 8:
                self.queue.page = int((len(self.queue.queue) - 2) / 7)
            self.queue.update()
            if self.queue.update_flag:
                self.queue.update_flag = False
                if self.msg is None:
                    self.msg =  await self.TextChannel.send(content = self.Text)
                    await self.msg.add_reaction('⏯️')
                    await self.msg.add_reaction('⏭️')
                    await self.msg.add_reaction('⬛')
                    await self.msg.add_reaction('◾')
                    await self.msg.add_reaction('🔀')
                    await self.msg.add_reaction('🔁')
                    await self.msg.add_reaction('▪️')
                    await self.msg.add_reaction('⬅️')
                    await self.msg.add_reaction('➡️')
                if self.msg.content != self.Text:
                    print(self.msg.content)
                    print(self.Text)
                    await self.msg.edit(content=self.Text)

                msg = await self.TextChannel.send(file=discord.File("tmpMusic.png", filename="tmpMusic.png"))
                await self.TextChannel.purge(limit=100, check=lambda x: x.id != msg.id and x.id != self.msg.id)
        except Exception as e:
            print(e)

    async def play(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        self.queue.append(Song(data))

    async def pause(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        self.VoiceClient.pause()
        self.queue.paused = True

    async def resume(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        self.VoiceClient.resume()
        self.queue.paused = False

    async def skip(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        if self.VoiceClient.is_playing():
            self.VoiceClient.stop()

    async def shufflen(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        print(self.queue.shuffle)
        self.queue.shuffle = not self.queue.shuffle
        print(self.queue.shuffle)

    async def shuffleq(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        x = [self.queue.queue[0]]
        self.queue.queue.remove(self.queue.queue[0])
        while len(self.queue.queue) > 0:
            i = randint(0, len(self.queue.queue)-1)
            x.append(self.queue.queue[i])
            self.queue.queue.remove(self.queue.queue[i])
        self.queue.queue.extend(x)

    async def stop(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        await self.VoiceClient.disconnect()

    async def repeatf(self, data):
        tchannel = client.get_channel(data[0]['TextChannelID'])
        if self.queue.repeat == data[0]['state'] + 1:
            self.queue.repeat = 0
        elif self.queue.queue[0] is not None:  
            self.queue.repeat = data[0]['state'] + 1
                  else:
            self.queue.repeat = data[0]['state'] + 1
        print(self.queue.repeat)
voice_clients = []
connect_status = -1
async def connect(voice_channel_id, text_channel_id, disconnectMSG, disconnectMSG2, enqueuedby):
    global connect_status
    try:
        VoiceChannel = client.get_channel(voice_channel_id)
        
        tchannel = client.get_channel(text_channel_id)
        c = VClientData(VoiceChannel, None, tchannel, disconnectMSG, disconnectMSG2, enqueuedby)
        
        c.role = await VoiceChannel.guild.create_role(name="tPlayerAccessRole")
        await tchannel.purge(limit=1000)
        await tchannel.set_permissions(
            c.role, overwrite=discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        manage_messages=False,
                        embed_links=False,
                        read_message_history=True,
                        mention_everyone=False,
                        manage_permissions=False,
                        attach_files=False,
                        add_reactions=False
                        ))
        VoiceClient = await VoiceChannel.connect()
        c.VoiceClient = VoiceClient
        for member in VoiceChannel.members:
            client.loop.create_task(member.add_roles(c.role))
        voice_clients.append(c)
    except Exception as e:
        print('returning ' + str([str(e)]))
        connect_status = 0
        return [str(e)]
    connect_status = 0
    return ["Success"]
async def connectCallback(data, bconn):
    print("connectCallback called")
    global connect_status
    connect_status = -1
    t = client.loop.create_task(connect(data[0]['VoiceChannelID'],
                                        data[0]['TextChannelID'],
                                        data[1]['disconnectMSG'],
                                        data[1]['disconnectMSG2'],
                                        data[1]['enqueuedby']))
    while True:
        if connect_status == 0:
            break
        await asyncio.sleep(0.25)
    return t.result()
async def generalFunc(func_name, data):
    for vclient in voice_clients:
        if vclient.VoiceChannel.id == data[0]['VoiceChannelID']:
            await getattr(vclient, func_name)(data)

async def playCallback(data, bconn):
    client.loop.create_task(generalFunc("play", data))

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


dead = False
async def queueHandler():
    global conn
    while True:
        for vclient in voice_clients:
            if not vclient.VoiceClient.is_connected():
                print("deleting bot")
                conn.POST(0, [vclient.VoiceChannel.id])
                voice_clients.remove(vclient)
                continue
            if not vclient.VoiceClient.is_paused():
                try:
                    await vclient.update()
                except Exception as e:
                    print(e)
                if time() - vclient.timestamp > 300:
                    conn.POST(0, [vclient.VoiceChannel.id])
                    await vclient.inactivityMSG()
                    await vclient.delete()
                    voice_clients.remove(vclient)
                    continue
            elif time() - vclient.timestamp > 600:
                conn.POST(0, [vclient.VoiceChannel.id])
                await vclient.inactivityMSG()
                await vclient.delete()
                voice_clients.remove(vclient)
                continue
            elif time() - vclient.timestampm > 60:
                conn.POST(0, [vclient.VoiceChannel.id])
                await vclient.inactivityMSG()
                await vclient.delete()
                voice_clients.remove(vclient)
                continue
            if vclient.VoiceChannel.id != vclient.VoiceClient.channel.id:
                print(vclient.VoiceChannel)
                print(vclient.VoiceClient.channel.id)
                try:
                    await vclient.VoiceClient.move_to(vclient.VoiceChannel)
                except:
                    await vclient.delete()
                    voice_clients.remove(vclient)
        await asyncio.sleep(1)
        if conn is not None:
            if conn.dead:
                for vc in voice_clients:
                    await vc.delete()
                    await vc.VoiceClient.disconnect()
                print('disconnected')
                conn.loop.stop()
                await asyncio.sleep(2.5)
                
                conn = None
                client.loop.create_task(client.close())
                global dead
                dead = True
                return
@client.event
async def on_ready():
    print("Вошёл как " + client.user.name + ". Мой ID: " + str(client.user.id))
    sock.connect(('localhost', 28484))
    global conn
    conn = bconn(sock, callbacks = [[get_user_id, 0], [guilds_list, 1], 
                                    [connectCallback, 0x100], [playCallback, 0x101],
                                    [pauseCallback, 0x103], [resumeCallback, 0x104], [skipCallback, 0x105],
                                    [shufflenCallback, 0x106], [shuffleqCallback, 0x107], [stopCallback, 0x108], 
                                    [repeatCallback, 0x109]])
@client.event
async def on_guild_join(guild):
    conn.POST(1, [guild.id])
@client.event
async def on_guild_remove(guild):
    conn.POST(2, [guild.id])
@client.event
async def on_reaction_add(reaction, user):
    for vclient in voice_clients:
        if vclient.TextChannel.id == reaction.message.channel.id:
            await vclient.on_reaction_add(reaction, user)
@client.event
async def on_voice_state_update(member, before, after):
    if member.id == client.user.id:
        return
    if before.channel is not None and after.channel is not None and before.channel.id == after.channel.id:
        return
    for vclient in voice_clients:
        if before.channel is not None and vclient.VoiceChannel.id == before.channel.id:
            client.loop.create_task(member.remove_roles(vclient.role))
            break
        elif after.channel is not None and vclient.VoiceChannel.id == after.channel.id:
            client.loop.create_task(member.add_roles(vclient.role))
            break
client.loop.create_task(queueHandler())
import threading
thread = threading.Thread(target=client.run, args=(sys.argv[1],))
thread.start()
import os
while client.loop.is_running():
    sleep(3)
    if dead == True:
        print('dead.')
        sleep(10)
        for task in asyncio.all_tasks(loop=client.loop):
            task.cancel()
        sleep(5)
        break

os._exit(0)

