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
class Song:
    def __init__(self, filepath, title, text_channel_id, np_str, userid):
        self.filepath = filepath
        self.title = title
        self.text_channel_id = text_channel_id
        self.np_str = np_str
        self.userid = userid

class VClientData:
    def __init__(self, VoiceChannel = None, VoiceClient = None, TextChannel = None, disconnectMSG = None,
                disconnectMSG2 = None, queue = [None], ffmpeg = None, role = None):
        self.VoiceClient = VoiceClient
        print(VoiceClient)
        self.VoiceChannel = VoiceChannel
        self.TextChannel = TextChannel
        self.disconnectMSG = disconnectMSG
        self.disconnectMSG2 = disconnectMSG2
        self.queue = queue
        print(queue)
        print(self.queue)
        self.ffmpeg = ffmpeg
        self.role = role
        self.timestamp = time()
        self.repeat = 0
        self.shuffle = 0

    async def delete(self):
        try:
            await self.VoiceClient.disconnect()
        except:
            pass
        try:
            await self.role.delete()
        except:
            pass
    def __del__(self):
        t = client.loop.create_task(self.delete())
        sleep(3)
    async def inactivityMSG(self):
        await client.get_channel(self.TextChannel).send(self.disconnectMSG.format(self.VoiceChannel.name))

    async def nooneMSG(self):
        await client.get_channel(self.TextChannel).send(self.disconnectMSG2.format(self.VoiceChannel.name))


    

    def __str__(self):
        a = ("VoiceChannel: " + str(self.VoiceChannel))
        a += ("\nVoiceClient: " + str(self.VoiceClient))
        a += ("\nTextChannel: " + str(self.TextChannel))
        a += ("\nshuffle: " + str(self.shuffle))
        a += ("\nrepeat: " + str(self.repeat))
        a += ("\nQueue: " + str(self.queue))
        return a

    async def update(self):
        if self.VoiceClient.is_playing():
            self.timestamp = time()
        elif len(self.queue) == 1:
            if self.repeat == 1:
                song = self.queue[0]
                if song is not None:
                    self.ffmpeg = discord.FFmpegPCMAudio(song.filepath)
                    self.VoiceClient.play(self.ffmpeg)
                    await client.get_channel(song.text_channel_id).send(song.np_str.format(song[1]))
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
                    rand = randint(1, len(self.queue)-1)
                    if len(self.queue) >= 4:
                        randint(1, len(self.queue)-2)
                    if len(self.queue) >= 8:
                        randint(1, len(self.queue)-4)
                    song = self.queue[rand]
                    self.queue.remove(self.queue[rand])
                    self.queue.insert(1,song)
                else:
                    song = self.queue[1]
                buf = self.queue[0]
                self.queue.remove(self.queue[0])
                self.queue.append(buf)
            print(song)
            self.ffmpeg = discord.FFmpegPCMAudio(song.filepath)
            self.VoiceClient.play(self.ffmpeg)
            await client.get_channel(song.text_channel_id).send(song.np_str.format(song.title))

    async def play(self, data):
        voice_channel_id, text_channel_id, filepath, title, track, alt_title, artist, channel, thumbnail, duration, userid, nowplaying, addedToQueue = data
        tchannel = client.get_channel(text_channel_id)
        await tchannel.send(addedToQueue.format(title, tchannel.guild.get_member(userid).mention))
        self.queue.append(Song(filepath, title, text_channel_id, nowplaying, userid))

    async def queuef(self, data):
        vc_id, tc_id, page, nothingInQueue, queue_for, queue_title, queue_error = data
        tchannel = client.get_channel(tc_id)
        embed = None
        if len(self.queue) < (page-1) * 10:
            string = "1"
            if len(self.queue) > 10:
                string += "-" + str(len(self.queue)/10 + 1)
            await tchannel.send(queue_error.format(page, string))
            return
        if len(self.queue) == 1 and self.queue[0] is None:
            embed = discord.Embed(title=nothingInQueue)
        else:
            embed = discord.Embed(title=queue_for.format(self.VoiceChannel.name, page))
            i = 0
            for song in self.queue[(page-1) * 10:(page) * 10]:
                embed.add_field(name=queue_title.format(str(i + 1), tchannel.guild.get_member(song.userid).nick), value = song.title, inline = False)
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
                await tchannel.send(msg.format(self.queue[0].title, self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
            else:
                await tchannel.send(msg.format("a song", self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        else:
            await tchannel.send(errormsg.format(tchannel.guild.get_member(userid).mention))

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
                await tchannel.send(msg.format(self.queue[0].title, self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
            elif self.repeat == 2:
                await tchannel.send(msgQ.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
        else:
            self.repeat = state + 1
            if self.repeat == 1:
                await tchannel.send(msgE.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))
            elif self.repeat == 2:
                await tchannel.send(msgQ.format(self.VoiceChannel.name, tchannel.guild.get_member(userid).mention))

voice_clients = []
async def connect(voice_channel_id, text_channel_id, disconnectMSG, disconnectMSG2):
    try:
        print(1)
        VoiceChannel = client.get_channel(voice_channel_id)
        print(2)

        c = VClientData(VoiceChannel, None, text_channel_id, disconnectMSG, disconnectMSG2)
        
        print(3)
        c.role = await VoiceChannel.guild.create_role(name="tPlayerAccessRole")
        print(4)
        tchannel = client.get_channel(text_channel_id)
        print(tchannel.name)
        print(5)
        print(tchannel.overwrites)
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
        print(6)
        VoiceClient = await VoiceChannel.connect()
        print(7)
        c.VoiceClient = VoiceClient
        print(8)
        for member in VoiceChannel.members:
            client.loop.create_task(member.add_roles(c.role))
        voice_clients.append(c)
    except Exception as e:
        print('returning ' + str([str(e)]))
        return [str(e)]
    return ["Success"]
async def connectCallback(data, bconn):
    print("connectCallback called")
    t = client.loop.create_task(connect(data[0], data[1], data[2], data[3]))
    await asyncio.sleep(3)
    while True:
        try:
            t.done()
            break
        except:
            print(e)
    return t.result()
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
                    print(vclient.timestamp)
                    conn.POST(0, [vclient.VoiceChannel.id])
                    await vclient.inactivityMSG()
                    await vclient.delete()
                    voice_clients.remove(vclient)
                    continue
            elif time() - vclient.timestamp > 600:
                print(vclient.timestamp)
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
                                    [connectCallback, 0x100], [playCallback, 0x101], [queueCallback, 0x102], 
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
async def on_voice_state_update(member, before, after):
    pass
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

