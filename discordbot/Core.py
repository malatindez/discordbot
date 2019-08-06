import sys
import os
import platform

if platform.system() == "Linux":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/DataBases/")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "/localisation/")
elif platform.system() == "Windows":
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\DataBases\\")
    sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)) + "\\localisation\\")
import discord
import asyncio
import generated_script
import time
import DataBase
import json
import Utils
plugins = []

import localisation
Localisation = localisation.Localisation()

client = discord.Client()
for plugin in generated_script.massive:
    g = plugin(Localisation)
    plugins.append(g)
    val = g.getUpdateFunctions()
    if val is not None:
        for function in val:
            client.loop.create_task(function(client))

db = DataBase.DB(plugins)

async def addGuildToDB(guild_id):
    # Создаем строку в JSON формате, в которой будут хранится данные
    #                       о включенных плагинах и каналах, к которым они подключены.
    enabled_plugins = "{"
    for plugin in plugins:
        enabled_plugins += "\"" + plugin.name + "\": []"
        if plugin != plugins[len(plugins)-1]:
            enabled_plugins += ","
        enabled_plugins+="\n"
    enabled_plugins += "}"
    # И добавляем её в базу данных.
    db.AddGuild(guild_id, "!", enabled_plugins)
    return
# Данная функция возвращает список плагинов, которые подключены к данному текстовому каналу
def getEnabledPluginsInChannel(channel_id, GuildEnabledPlugins):
    returnValue = []
    for Plugin in GuildEnabledPlugins:
        for channel in GuildEnabledPlugins[Plugin]:
            if channel == channel_id:
                returnValue.append(Plugin)
    return returnValue



async def admin_message(command, message, client, guildData, GuildEnabledPlugins):
    await message.delete(delay = 5)
    lang =  Utils.getChannelLanguage(db, message.channel.id)
    def lGetText(value):
            return Localisation.getText("AdminCommands", value, lang)
    if(command[0] == "help"):
        embed = discord.Embed(
            title = lGetText("helpTitle"),
            color = 0xff0000)
        embed.add_field(name="help", value=lGetText("help"), inline=False)
        embed.add_field(name="listOfPackages", value=lGetText("listOfPackages"), inline=False)
        embed.add_field(name=lGetText("connectPackageCmd"), value=lGetText("connectPackage"), inline=False)
        embed.add_field(name=lGetText("disconnectPackageCmd"), value=lGetText("disconnectPackage"), inline=False)
        embed.add_field(name="listOfLanguages", value=lGetText("listOfLanguages"), inline=False)
        embed.add_field(name=lGetText("changeLanguageCmd"), value=lGetText("changeLanguage"), inline=False)
        embed.add_field(name=lGetText("changePrefixCmd"), value=lGetText("changePrefix"), inline=False)
        await message.channel.send(embed=embed, delete_after = 30)
    elif command[0] == "listofpackages":
        embed = discord.Embed(
            title = lGetText("listOfPackagesTitle"),
            color = 0xaa00aa)
        
        EnabledPluginsInChannel = getEnabledPluginsInChannel(message.channel.id, GuildEnabledPlugins)
        for plugin in plugins:
            if plugin.name in EnabledPluginsInChannel:
                print(EnabledPluginsInChannel)
                embed.add_field(name=plugin.name + "["+ lGetText("connected") + "]", value=plugin.getDescription(message.channel.id), inline=True)
            else:
                embed.add_field(name=plugin.name, value=plugin.getDescription(message.channel.id), inline=True)

        await message.channel.send(embed=embed, delete_after = 30)
    elif command[0] == "connectpackage":
        plugin_channels = json.loads(guildData[0][2])
        try:
            for element in plugin_channels[command[1][0]]:
                if element == message.channel.id:
                    await message.channel.send(lGetText("connectPackageFail"))
                    return
            plugin_channels[command[1][0]].append(message.channel.id)
        except:
            await message.channel.send(lGetText("connectPackageFailWN"))
            return       
        db.EditGuild(message.guild.id, guildData[0][1], json.dumps(plugin_channels))

        await message.channel.send(lGetText("connectPackageSuccess"), delete_after = 30)
    elif command[0] == "disconnectpackage":
        plugin_channels = json.loads(guildData[0][2])
        try:
            for element in plugin_channels[command[1][0]]:
                if element == message.channel.id:
                    plugin_channels[command[1][0]].remove(element)
                    db.EditGuild(message.guild.id, guildData[0][1], json.dumps(plugin_channels))
                    await message.channel.send(lGetText("disconnectPackageSuccess"), delete_after = 30)
                    return
        except:
            await message.channel.send(lGetText("connectPackageFailWN"), delete_after = 30)
        await message.channel.send(lGetText("disconnectPackageFail"), delete_after = 30)
    elif command[0] == "listoflanguages":
        embed = discord.Embed(
            title = lGetText("listOfAvailableLanguagesTitle"),
            color = 0x880088)
        for element in Localisation.getAvailableLanguages():
            embed.add_field(name=element, value=Localisation.getText("description", "name", element), inline=True)
        await message.channel.send(embed=embed, delete_after = 30)
    elif command[0] == "changelanguage":
        for element in Localisation.getAvailableLanguages():
            if element == command[1][0]:
                db.UPDATE("ChannelsAndLanguages", [["language", element]], "channelID = " + str(message.channel.id))
                await message.channel.send(lGetText("changeLanguageSuccess"), delete_after = 30)
                return
        await message.channel.send(lGetText("changeLanguageWL"), delete_after = 30)
    elif command[0] == "changeprefix":
        try:
            if command[1][0] == guildData[0][1]:
                await message.channel.send(lGetText("changePrefixFailWN"), delete_after = 30)
                return
            if len(command[1][0])!=1:
                await message.channel.send(lGetText("changePrefixFail"), delete_after = 30)
                return
            db.UPDATE("Guilds", [["prefix",command[1][0]]], "id = " + str(message.guild.id))
            await message.channel.send(lGetText("changePrefixSuccess").format(command[1][0]), delete_after = 30)
        except:
            await message.channel.send(lGetText("changePrefixFail"), delete_after = 30)

@client.event
async def on_message(message):

    

    # Пропуск сообщений, отправляемых ботом.
    if(message.author == client.user):
        return
    
    # Получаем данные в базе данных о гильдии, в которой было написано это сообщение.
    data = db.GetGuildData(message.guild.id)
    if len(data) == 0:
        await addGuildToDB(message.guild.id)
        data = db.GetGuildData(message.guild.id)
    
    # Получаем список плагинов, которые подключены к этой гильдии
    GuildEnabledPlugins = json.loads(data[0][2])

    # Если первый символ сообщения не соответствует префиксу, установленному в этой гильдии - return
    if message.content[0]!=data[0][1]:
        return

    # Превращаем сообщение "!name param1 param2 param3 ..." в список [name, [param1, param2, param3, ...]]
    command = Utils.getCommand(message.content)
    
    # Ищем команду name
    EnabledPluginsInChannel = getEnabledPluginsInChannel(message.channel.id, GuildEnabledPlugins)
    for plugin in plugins:
        if plugin.name in EnabledPluginsInChannel:
            for Command in plugin.getCommands():
                if Command[0] == command[0]:
                    await Command[1](command[1], message, client)
                    return

    # Если команда не была найдена, проверяем - является ли одна командой администратора.
    if message.author.permissions_in(message.channel).value & 8 == 8:
        await admin_message(command, message, client, data, GuildEnabledPlugins)

async def getPluginByChannelId(channelID, guildID):
    data = db.GetGuildData(guildID)
    if len(data) == 0:
        await addGuildToDB(guildID)
        return None
    GuildEnabledPlugins = json.loads(data[0][2])
    for Plugin in GuildEnabledPlugins:
        for channel in GuildEnabledPlugins[Plugin]:
            if channel == channelID:
                for plugin in plugins:
                    if plugin.name == Plugin:
                        return plugin
    return None

@client.event
async def on_raw_message_delete(payload):
    p = await getPluginByChannelId(payload.channel_id, payload.guild_id) 
    if p is not None:
        await p.on_raw_message_delete(payload)
@client.event
async def on_message_edit(before, after):
    p = await getPluginByChannelId(before.channel.id, before.guild.id) 
    if p is not None:
        await p.on_message_edit(before, after)
@client.event
async def on_reaction_add(reaction, user):
    p = await getPluginByChannelId(reaction.message.channel.id, reaction.guild.id) 
    if p is not None:
        await p.on_reaction_add(reaction, user)
@client.event
async def on_raw_reaction_add(payload):
    p = await getPluginByChannelId(payload.channel_id, payload.guild_id) 
    if p is not None:
        await p.on_raw_reaction_add(payload)
@client.event
async def on_reaction_remove(reaction, user):
    p = await getPluginByChannelId(reaction.message.channel.id, reaction.guild.id) 
    if p is not None:
        await p.on_reaction_remove(reaction, user)
@client.event
async def on_raw_reaction_remove(payload):
    p = await getPluginByChannelId(payload.channel_id, payload.guild_id) 
    if p is not None:
        await p.on_raw_reaction_remove(payload)
@client.event
async def on_reaction_clear(message, reactions):
    p = await getPluginByChannelId(message.channel.id, message.guild.id) 
    if p is not None:
        await p.on_reaction_clear(before, after)
@client.event
async def on_raw_reaction_clear(payload):
    p = await getPluginByChannelId(payload.channel_id, payload.guild_id) 
    if p is not None:
        await p.on_raw_reaction_clear(payload)
@client.event
async def on_private_channel_delete(channel):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_private_channel_delete(channel)
@client.event
async def on_private_channel_create(channel):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_private_channel_create(channel)
@client.event
async def on_private_channels_update(before, after):
    p = await getPluginByChannelId(before.id, before.guild.id) 
    if p is not None:
        await p.on_private_channels_update(before, after)
@client.event
async def on_private_channel_pins_update(channel, last_pin):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_private_channel_pins_update(channel, last_pin)
@client.event
async def on_guild_channel_delete(channel):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_guild_channel_delete(channel)
@client.event
async def on_guild_channel_create(channel):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_guild_channel_create(channel)
@client.event
async def on_guild_channel_update(before, after):
    p = await getPluginByChannelId(before.id, before.guild.id) 
    if p is not None:
        await p.on_guild_channel_update(before, after)
@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    p = await getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_guild_channel_pins_update(channel, last_pin)

@client.event
async def on_guild_integrations_update(guild):
    for plugin in plugins:
        await plugin.on_guild_integrations_update(guild)

@client.event
async def on_webhoooks_update(channel):
    p = getPluginByChannelId(channel.id, channel.guild.id) 
    if p is not None:
        await p.on_webhoooks_update(channel)

@client.event
async def on_member_join(member):
    for plugin in plugins:
        await plugin.on_member_join(member)

@client.event
async def on_member_remove(member):
    for plugin in plugins:
        await plugin.on_member_remove(member)

@client.event
async def on_member_update(before, after):
    for plugin in plugins:
        await plugin.on_member_update(before, after)

@client.event
async def on_guild_join(guild):
    for plugin in plugins:
        await plugin.on_guild_join(guild)

@client.event
async def on_guild_remove(guild):
    for plugin in plugins:
        await plugin.on_guild_remove(guild)

@client.event
async def on_guild_update(guild):
    for plugin in plugins:
        await plugin.on_guild_update(guild)

@client.event
async def on_guild_role_create(role):
    for plugin in plugins:
        await plugin.on_guild_role_create(role)

@client.event
async def on_guild_role_delete(role):
    for plugin in plugins:
        await plugin.on_guild_role_delete(role)

@client.event
async def on_guild_role_update(before, after):
    for plugin in plugins:
        await plugin.on_guild_role_update(before, after)

@client.event
async def on_guild_emojis_update(guild, before, after):
    for plugin in plugins:
        await plugin.on_guild_emojis_update(guild, before, after)

@client.event
async def on_voice_state_update(member, before, after):
    for plugin in plugins:
        await plugin.on_voice_state_update(member, before, after)

@client.event
async def on_member_ban(guild, user):
    for plugin in plugins:
        await plugin.on_member_ban(guild, user)

@client.event
async def on_member_unban(guild, user):
    for plugin in plugins:
        await plugin.on_member_ban(guild, user)

@client.event
async def on_ready():
    print("Вошёл как " + client.user.name + ". Мой ID: " + str(client.user.id))

token = ""
try:
    if platform.system() == "Linux":
        f = open('../token'); token = f.readline(); f.close();
    elif platform.system() == "Windows":
        f = open('..\\token'); token = f.readline(); f.close()
except:
    print("Добавьте токен в папку выше")
    exit()

client.run(token)